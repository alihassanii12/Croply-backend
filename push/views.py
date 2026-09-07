from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PushSubscription
from .serializers import PushSubscriptionSerializer


class PushSubscribeView(APIView):
    """
    POST /api/push/subscribe/
    Body: { endpoint, p256dh, auth }
    Saves or updates the subscription for the current user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        endpoint = request.data.get('endpoint', '').strip()
        p256dh   = request.data.get('p256dh', '').strip()
        auth     = request.data.get('auth', '').strip()

        if not all([endpoint, p256dh, auth]):
            return Response(
                {'detail': 'endpoint, p256dh and auth are required.'},
                status=400,
            )

        sub, _ = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user':   request.user,
                'p256dh': p256dh,
                'auth':   auth,
            },
        )
        return Response(
            PushSubscriptionSerializer(sub).data,
            status=status.HTTP_201_CREATED,
        )


class PushUnsubscribeView(APIView):
    """
    POST /api/push/unsubscribe/
    Body: { endpoint }
    Removes the subscription.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        endpoint = request.data.get('endpoint', '').strip()
        PushSubscription.objects.filter(
            endpoint=endpoint, user=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
