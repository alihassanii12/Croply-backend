from rest_framework import viewsets

from .models import Disease
from .serializers import DiseaseSerializer


class DiseaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
