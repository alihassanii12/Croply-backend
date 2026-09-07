from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile


# ── Profile ────────────────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'location', 'bio', 'avatar_url']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile']


# ── Register ───────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, default='')
    last_name = serializers.CharField(max_length=150, default='')
    role = serializers.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        default=UserProfile.ROLE_FARMER,
    )
    phone = serializers.CharField(max_length=30, default='', allow_blank=True)
    location = serializers.CharField(max_length=255, default='', allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        role = validated_data.pop('role')
        phone = validated_data.pop('phone', '')
        location = validated_data.pop('location', '')
        password = validated_data.pop('password')
        email = validated_data['email']

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )

        UserProfile.objects.create(
            user=user,
            role=role,
            phone=phone,
            location=location,
        )

        return user


# ── Login ──────────────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        email = data['email'].lower()
        user = authenticate(username=email, password=data['password'])
        if not user:
            try:
                u = User.objects.get(email__iexact=email)
                user = authenticate(username=u.username, password=data['password'])
            except User.DoesNotExist:
                pass
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account has been disabled.')
        data['user'] = user
        return data


# ── Token response helper ──────────────────────────────────────────────────

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ── Google OAuth ───────────────────────────────────────────────────────────

class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    role = serializers.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=False,
        allow_null=True,
    )


# ── Profile update ─────────────────────────────────────────────────────────

class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name',
            'phone', 'location', 'bio', 'avatar_url',
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
