from rest_framework import serializers

from accounts.models import UserProfile
from .models import ChatMessage, TypingStatus


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name   = serializers.SerializerMethodField()
    sender_avatar = serializers.SerializerMethodField()
    is_mine       = serializers.SerializerMethodField()
    image_url     = serializers.SerializerMethodField()
    voice_url     = serializers.SerializerMethodField()

    class Meta:
        model  = ChatMessage
        fields = [
            'id', 'listing', 'sender', 'recipient',
            'sender_name', 'sender_avatar', 'is_mine',
            'message_type', 'body', 'image', 'voice', 'voice_duration',
            'image_url', 'voice_url',
            'status', 'is_read', 'read_at', 'delivered_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'sender', 'sender_name', 'sender_avatar',
            'is_mine', 'status', 'is_read', 'read_at', 'delivered_at',
            'created_at', 'updated_at', 'image_url', 'voice_url',
        ]

    def get_sender_name(self, obj):
        name = obj.sender.get_full_name()
        return name if name.strip() else obj.sender.email

    def get_sender_avatar(self, obj):
        try:
            return obj.sender.profile.avatar_url or ''
        except UserProfile.DoesNotExist:
            return ''

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and obj.sender == request.user)
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_voice_url(self, obj):
        if obj.voice:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.voice.url)
        return None


class TypingStatusSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TypingStatus
        fields = ['id', 'listing', 'user', 'user_name', 'is_typing', 'last_typed_at']
        read_only_fields = ['id', 'user', 'user_name', 'last_typed_at']
    
    def get_user_name(self, obj):
        name = obj.user.get_full_name()
        return name if name.strip() else obj.user.email
