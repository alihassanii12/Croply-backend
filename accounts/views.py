import requests as http_requests

from django.conf import settings
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView  # re-export

from .models import UserProfile
from .serializers import (
    GoogleAuthSerializer,
    LoginSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
    get_tokens_for_user,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response(
            {'user': UserSerializer(user).data, **tokens},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({'user': UserSerializer(user).data, **tokens})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=404)

        serializer = ProfileUpdateSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class GoogleAuthView(APIView):
    """
    POST { id_token, role? }
    Verifies Google ID-token via Google's tokeninfo endpoint,
    creates/retrieves the user, returns JWT tokens.
    If role is not provided, the user will be created without a role.
    """
    permission_classes = [AllowAny]

    GOOGLE_TOKEN_INFO_URL = 'https://oauth2.googleapis.com/tokeninfo'

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token = serializer.validated_data['id_token']
        role = serializer.validated_data.get('role')

        # Verify the token with Google
        try:
            resp = http_requests.get(
                self.GOOGLE_TOKEN_INFO_URL,
                params={'id_token': id_token},
                timeout=10,
            )
            resp.raise_for_status()
            payload = resp.json()
        except Exception:
            return Response(
                {'detail': 'Could not verify Google token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate audience
        client_id = settings.GOOGLE_CLIENT_ID
        if client_id and payload.get('aud') != client_id:
            return Response(
                {'detail': 'Token audience mismatch.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        google_id = payload.get('sub')
        email = payload.get('email', '').lower()
        first_name = payload.get('given_name', '')
        last_name = payload.get('family_name', '')
        avatar_url = payload.get('picture', '')

        if not email or not google_id:
            return Response(
                {'detail': 'Invalid Google token payload.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create user
        profile = UserProfile.objects.filter(google_id=google_id).first()
        if profile:
            user = profile.user
        else:
            user, created = User.objects.get_or_create(
                email__iexact=email,
                defaults={
                    'username': email,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                },
            )
            try:
                profile = user.profile
                profile.google_id = google_id
                if avatar_url:
                    profile.avatar_url = avatar_url
                profile.save()
            except UserProfile.DoesNotExist:
                # If role is provided, use it. Otherwise create without role.
                profile = UserProfile.objects.create(
                    user=user,
                    google_id=google_id,
                    avatar_url=avatar_url,
                )
                if role:
                    profile.role = role
                    profile.save()

        tokens = get_tokens_for_user(user)
        response_data = {'user': UserSerializer(user).data, **tokens}
        
        # Add a flag to indicate if user needs role selection
        if not profile.role:
            response_data['needs_role'] = True
            # Return 206 Partial Content when user needs to select role
            return Response(response_data, status=status.HTTP_206_PARTIAL_CONTENT)
        
        return Response(response_data)


class SetRoleView(APIView):
    """
    PATCH { role }
    Sets the role for a Google-authenticated user after Google auth.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=404)
        
        # Check if this is a Google user (or any user that needs role)
        role = request.data.get('role')
        if role not in [UserProfile.ROLE_FARMER, UserProfile.ROLE_BUYER]:
            return Response(
                {'detail': f'Role must be either {UserProfile.ROLE_FARMER} or {UserProfile.ROLE_BUYER}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        profile.role = role
        profile.save()
        
        tokens = get_tokens_for_user(request.user)
        return Response({'user': UserSerializer(request.user).data, **tokens})


class DeleteAccountView(APIView):
    """
    DELETE - Delete user account and all associated data
    Requires text confirmation for security (no password needed)
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        # Get confirmation text from request
        confirmation_text = request.data.get('confirmation_text')
        
        if not confirmation_text or confirmation_text != "DELETE MY ACCOUNT":
            return Response(
                {'detail': 'Please type "DELETE MY ACCOUNT" exactly to confirm deletion.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Delete user (this will cascade delete profile due to CASCADE relationship)
            request.user.delete()
            return Response(
                {'detail': 'Account deleted successfully.'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'detail': f'Error deleting account: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
