from django.contrib.auth.models import User
from django.db import models

from marketplace.models import Listing


class ChatMessage(models.Model):
    """A message in a buyer-seller conversation about a listing."""
    
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image Message'),
        ('voice', 'Voice Message'),
    ]
    
    MESSAGE_STATUS = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]

    listing   = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='messages'
    )
    sender    = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages'
    )
    
    # Message content
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    body      = models.TextField(blank=True)  # For text messages
    
    # Media fields
    image     = models.ImageField(upload_to='chat/images/', null=True, blank=True)
    voice     = models.FileField(upload_to='chat/voice/', null=True, blank=True)
    voice_duration = models.IntegerField(null=True, blank=True, help_text='Duration in seconds')
    
    # Status tracking
    status    = models.CharField(max_length=10, choices=MESSAGE_STATUS, default='sent')
    is_read   = models.BooleanField(default=False)
    read_at   = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'[{self.listing_id}] {self.sender} → {self.recipient} ({self.message_type})'


class TypingStatus(models.Model):
    """Track when users are typing in a conversation."""
    
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='typing_statuses'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='typing_statuses'
    )
    is_typing = models.BooleanField(default=False)
    last_typed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['listing', 'user']
        
    def __str__(self):
        return f'{self.user} typing in listing {self.listing_id}'
