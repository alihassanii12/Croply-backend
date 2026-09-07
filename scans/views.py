from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsFarmer
from diseases.models import Disease

from .models import Scan
from .serializers import ScanSerializer
from .services import InferenceError, predict_image


class ScanViewSet(viewsets.ModelViewSet):
    serializer_class = ScanSerializer
    permission_classes = [IsAuthenticated, IsFarmer]

    def get_queryset(self):
        return Scan.objects.select_related('disease').filter(
            user=self.request.user
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        scan = serializer.save(user=request.user)

        inference_error = None

        try:
            result = predict_image(scan.image)
        except InferenceError as exc:
            inference_error = str(exc)
        else:
            scan.predicted_class = result.get('predicted_class', '')
            scan.plant = result.get('plant', '')
            scan.disease_name = result.get('disease', '')
            scan.confidence = result.get('confidence')
            scan.top_predictions = result.get('top_predictions', [])
            scan.disease = Disease.objects.filter(
                name=scan.predicted_class
            ).first()
            scan.save()

        data = self.get_serializer(scan).data

        if inference_error:
            data['inference_error'] = inference_error

        return Response(data, status=status.HTTP_201_CREATED)
