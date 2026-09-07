from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsFarmer

from .models import Crop
from .serializers import CropSerializer


class CropViewSet(viewsets.ModelViewSet):
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated, IsFarmer]

    def get_queryset(self):
        # Only crops belonging to this farmer's farms
        return Crop.objects.select_related('farm').filter(
            farm__owner=self.request.user
        )
