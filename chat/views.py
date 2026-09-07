from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from marketplace.models import Listing
from .models import ChatMessage, TypingStatus
from .serializers import ChatMessageSerializer, TypingStatusSerializer


class ChatMessageListView(APIView):
    """
    GET  /api/chat/?listing=<id>   — fetch all messages for this listing
    POST /api/chat/?listing=<id>   — send a message (text, image, or voice)

    Buyer messages go to the listing's seller.
    Seller messages go to the buyer (must pass ?buyer=<user_id> for seller).
    Both parties see the full thread for this listing.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get_listing(self, listing_id):
        try:
            return Listing.objects.get(pk=listing_id, is_active=True)
        except Listing.DoesNotExist:
            return None

    def get(self, request):
        listing_id = request.query_params.get('listing')
        if not listing_id:
            return Response({'detail': 'listing param required.'}, status=400)

        listing = self._get_listing(listing_id)
        if not listing:
            return Response({'detail': 'Listing not found.'}, status=404)

        user = request.user
        # Retrieve messages where user is either sender or recipient
        messages = ChatMessage.objects.filter(
            listing=listing
        ).filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('sender', 'sender__profile')

        # Mark incoming messages as delivered and read
        unread_messages = messages.filter(recipient=user, is_read=False)
        for msg in unread_messages:
            if not msg.delivered_at:
                msg.delivered_at = timezone.now()
                msg.status = 'delivered'
            msg.is_read = True
            msg.read_at = timezone.now()
            msg.status = 'read'
        ChatMessage.objects.bulk_update(unread_messages, ['is_read', 'read_at', 'delivered_at', 'status'])

        serializer = ChatMessageSerializer(
            messages, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        listing_id = request.query_params.get('listing')
        if not listing_id:
            return Response({'detail': 'listing param required.'}, status=400)

        listing = self._get_listing(listing_id)
        if not listing:
            return Response({'detail': 'Listing not found.'}, status=404)

        user = request.user
        seller = listing.seller

        # Determine recipient
        if user == seller:
            # Seller replying to a buyer — buyer_id must be provided
            buyer_id = request.data.get('recipient')
            if not buyer_id:
                return Response(
                    {'detail': 'recipient (buyer id) required for seller reply.'},
                    status=400,
                )
            from django.contrib.auth.models import User as DjangoUser
            try:
                recipient = DjangoUser.objects.get(pk=buyer_id)
            except DjangoUser.DoesNotExist:
                return Response({'detail': 'Recipient not found.'}, status=404)
        else:
            # Buyer messaging the seller
            recipient = seller

        # Determine message type and content
        message_type = request.data.get('message_type', 'text')
        body = request.data.get('body', '').strip()
        image = request.FILES.get('image')
        voice = request.FILES.get('voice')
        voice_duration = request.data.get('voice_duration')

        # Validate based on message type
        if message_type == 'text' and not body:
            return Response({'detail': 'Message body is required for text messages.'}, status=400)
        elif message_type == 'image' and not image:
            return Response({'detail': 'Image file is required for image messages.'}, status=400)
        elif message_type == 'voice' and not voice:
            return Response({'detail': 'Voice file is required for voice messages.'}, status=400)

        msg = ChatMessage.objects.create(
            listing=listing,
            sender=user,
            recipient=recipient,
            message_type=message_type,
            body=body,
            image=image,
            voice=voice,
            voice_duration=voice_duration,
            status='sent',
        )

        # Create in-app notification for recipient
        from notifications.models import Notification
        sender_name = user.get_full_name() or user.email
        
        if message_type == 'text':
            notif_msg = f'Re: {listing.title} — "{body[:80]}"'
        elif message_type == 'image':
            notif_msg = f'Re: {listing.title} — Image'
        elif message_type == 'voice':
            notif_msg = f'Re: {listing.title} — Voice message'
        else:
            notif_msg = f'Re: {listing.title}'
            
        Notification.objects.create(
            user=recipient,
            title=f'New message from {sender_name}',
            message=notif_msg,
        )

        return Response(
            ChatMessageSerializer(msg, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ChatThreadsView(APIView):
    """
    GET /api/chat/threads/
    Returns a list of unique listing-threads the current user is part of.
    Fixed to group by (listing_id, other_user_id) instead of just listing_id
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get all messages where user is involved
        messages = ChatMessage.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('listing', 'sender', 'recipient')

        # Group by (listing_id, other_user_id) to create unique threads
        threads_dict = {}
        
        for msg in messages:
            listing = msg.listing
            if not listing or not listing.is_active:
                continue
                
            # Determine the other user in this conversation
            other_user = msg.recipient if msg.sender == user else msg.sender
            
            # Create unique thread key
            thread_key = (listing.id, other_user.id)
            
            if thread_key not in threads_dict:
                threads_dict[thread_key] = {
                    'listing_id': listing.id,
                    'listing_title': listing.title,
                    'other_user_id': other_user.id,
                    'other_user_name': other_user.get_full_name() or other_user.email,
                    'last_message': '',
                    'last_message_type': 'text',
                    'last_at': '',
                    'unread': 0,
                    'messages': []
                }
            
            # Add message to thread
            threads_dict[thread_key]['messages'].append(msg)
        
        # Process each thread to get latest message and unread count
        threads = []
        for thread_data in threads_dict.values():
            messages_in_thread = sorted(thread_data['messages'], key=lambda m: m.created_at)
            
            if messages_in_thread:
                last_msg = messages_in_thread[-1]
                thread_data['last_message'] = last_msg.body if last_msg.message_type == 'text' else ''
                thread_data['last_message_type'] = last_msg.message_type
                thread_data['last_at'] = last_msg.created_at.isoformat()
                
                # Count unread messages (where current user is recipient)
                unread_count = sum(1 for m in messages_in_thread 
                                 if m.recipient == user and not m.is_read)
                thread_data['unread'] = unread_count
            
            # Remove messages list from response (we don't need it in the API)
            del thread_data['messages']
            threads.append(thread_data)

        # Sort by last message time (newest first)
        threads.sort(key=lambda t: t['last_at'], reverse=True)
        return Response(threads)


class MessageStatusView(APIView):
    """
    PATCH /api/chat/<message_id>/status/
    Update message status (delivered or read)
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, message_id):
        try:
            message = ChatMessage.objects.get(pk=message_id)
        except ChatMessage.DoesNotExist:
            return Response({'detail': 'Message not found.'}, status=404)
        
        # Only recipient can update status
        if message.recipient != request.user:
            return Response({'detail': 'Not authorized.'}, status=403)
        
        new_status = request.data.get('status')
        if new_status not in ['delivered', 'read']:
            return Response({'detail': 'Invalid status.'}, status=400)
        
        if new_status == 'delivered' and not message.delivered_at:
            message.delivered_at = timezone.now()
            message.status = 'delivered'
        elif new_status == 'read':
            if not message.delivered_at:
                message.delivered_at = timezone.now()
            message.read_at = timezone.now()
            message.is_read = True
            message.status = 'read'
        
        message.save()
        
        return Response(
            ChatMessageSerializer(message, context={'request': request}).data
        )


class TypingStatusView(APIView):
    """
    POST /api/chat/typing/
    Update typing status for a conversation
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        listing_id = request.data.get('listing')
        is_typing = request.data.get('is_typing', False)
        
        if not listing_id:
            return Response({'detail': 'listing param required.'}, status=400)
        
        try:
            listing = Listing.objects.get(pk=listing_id, is_active=True)
        except Listing.DoesNotExist:
            return Response({'detail': 'Listing not found.'}, status=404)
        
        typing_status, created = TypingStatus.objects.update_or_create(
            listing=listing,
            user=request.user,
            defaults={'is_typing': is_typing}
        )
        
        return Response(
            TypingStatusSerializer(typing_status, context={'request': request}).data
        )
    
    def get(self, request):
        """Get typing status for a conversation"""
        listing_id = request.query_params.get('listing')
        
        if not listing_id:
            return Response({'detail': 'listing param required.'}, status=400)
        
        try:
            listing = Listing.objects.get(pk=listing_id, is_active=True)
        except Listing.DoesNotExist:
            return Response({'detail': 'Listing not found.'}, status=404)
        
        # Get typing statuses for this listing (exclude current user)
        typing_statuses = TypingStatus.objects.filter(
            listing=listing,
            is_typing=True
        ).exclude(user=request.user).select_related('user')
        
        # Filter out stale typing indicators (older than 5 seconds)
        from datetime import timedelta
        five_seconds_ago = timezone.now() - timedelta(seconds=5)
        typing_statuses = typing_statuses.filter(last_typed_at__gte=five_seconds_ago)
        
        return Response(
            TypingStatusSerializer(typing_statuses, many=True, context={'request': request}).data
        )
