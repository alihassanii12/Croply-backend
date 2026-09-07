from rest_framework import serializers

from diseases.serializers import DiseaseSerializer

from .models import Scan


class ScanSerializer(serializers.ModelSerializer):
    disease_detail = DiseaseSerializer(
        source='disease',
        read_only=True,
    )

    class Meta:
        model = Scan
        fields = [
            'id',
            'image',
            'predicted_class',
            'plant',
            'disease_name',
            'confidence',
            'top_predictions',
            'disease',
            'disease_detail',
            'created_at',
        ]
        read_only_fields = [
            'predicted_class',
            'plant',
            'disease_name',
            'confidence',
            'top_predictions',
            'disease',
        ]
