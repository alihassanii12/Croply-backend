from django.urls import path
from .views import ChatMessageListView, ChatThreadsView, MessageStatusView, TypingStatusView

urlpatterns = [
    path('',        ChatMessageListView.as_view(), name='chat-messages'),
    path('threads/', ChatThreadsView.as_view(),    name='chat-threads'),
    path('<int:message_id>/status/', MessageStatusView.as_view(), name='message-status'),
    path('typing/', TypingStatusView.as_view(), name='typing-status'),
]
