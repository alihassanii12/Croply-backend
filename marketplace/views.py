from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsFarmerOrReadOnly, IsOwnerOrReadOnly

from .models import Listing
from .serializers import ListingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    - GET (list/retrieve): any authenticated user (farmer or buyer)
    - POST: farmers only
    - PATCH/PUT/DELETE: farmer + must be the listing owner
    """
    serializer_class = ListingSerializer

    def get_queryset(self):
        return Listing.objects.filter(is_active=True).select_related('seller')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        if self.action == 'create':
            return [IsAuthenticated(), IsFarmerOrReadOnly()]
        # update / partial_update / destroy
        return [IsAuthenticated(), IsFarmerOrReadOnly(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
