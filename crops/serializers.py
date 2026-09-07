from rest_framework import serializers

from .models import Crop


class CropSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(
        source='farm.name',
        read_only=True,
    )

    class Meta:
        model = Crop
        fields = [
            'id',
            'name',
            'farm',
            'farm_name',
            'planted_date',
            'status',
            'notes',
            'created_at',
        ]
