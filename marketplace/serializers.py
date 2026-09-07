from rest_framework import serializers

from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    seller_name = serializers.SerializerMethodField(read_only=True)
    seller_avatar = serializers.SerializerMethodField(read_only=True)
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    is_mine = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'price',
            'quantity',
            'unit',
            'contact',
            'is_active',
            'seller_id',
            'seller_name',
            'seller_avatar',
            'is_mine',
            'created_at',
        ]
        read_only_fields = [
            'seller_id', 'seller_name', 'seller_avatar', 'is_mine', 'created_at'
        ]

    def get_seller_name(self, obj):
        if obj.seller:
            name = obj.seller.get_full_name()
            return name if name.strip() else obj.seller.email
        return ''

    def get_seller_avatar(self, obj):
        if obj.seller:
            try:
                return obj.seller.profile.avatar_url or ''
            except Exception:
                pass
        return ''

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.seller == request.user
        return False
