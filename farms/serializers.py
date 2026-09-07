from rest_framework import serializers

from .models import Farm


class FarmSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Farm
        fields = [
            'id',
            'name',
            'location',
            'size_hectares',
            'description',
            'owner_name',
            'created_at',
        ]
        read_only_fields = ['owner_name', 'created_at']

    def get_owner_name(self, obj):
        if obj.owner:
            return obj.owner.get_full_name() or obj.owner.email
        return ''
