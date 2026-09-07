from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsFarmer, IsOwnerOrReadOnly

from .models import Farm
from .serializers import FarmSerializer


class FarmViewSet(viewsets.ModelViewSet):
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated, IsFarmer]

    def get_queryset(self):
        return Farm.objects.filter(owner=self.request.user)

    def get_permissions(self):
        perms = [IsAuthenticated(), IsFarmer()]
        if self.action in ('update', 'partial_update', 'destroy'):
            perms.append(IsOwnerOrReadOnly())
        return perms

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
