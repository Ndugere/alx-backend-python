from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

# ViewSet for Conversations
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    # ✅ Enables search capability on the 'name' field
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        # Return only conversations the logged-in user is a participant of
        return self.queryset.filter(participants=self.request.user)

    def perform_create(self, serializer):
        # Automatically add the logged-in user as a participant when a new conversation is created
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

# ViewSet for Messages
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter messages based on the conversation ID passed in the URL query params
        conversation_id = self.request.query_params.get('conversation')
        if conversation_id:
            return self.queryset.filter(conversation__id=conversation_id, conversation__participants=self.request.user)
        return self.queryset.none()

    def perform_create(self, serializer):
        # Ensure the message is sent by the logged-in user
        serializer.save(sender=self.request.user)
