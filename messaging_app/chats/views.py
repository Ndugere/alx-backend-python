from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint to list, retrieve, and create conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return conversations the user is part of
        return self.queryset.filter(participants=self.request.user)

    def perform_create(self, serializer):
        # Automatically add the requesting user to the conversation
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint to send and view messages in a conversation.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optionally filter by conversation ID
        conversation_id = self.request.query_params.get('conversation')
        if conversation_id:
            return self.queryset.filter(conversation__id=conversation_id)
        return self.queryset.none()

    def perform_create(self, serializer):
        # The sender is always the logged-in user
        conversation_id = self.request.data.get('conversation')
        if not conversation_id:
            raise serializers.ValidationError("Conversation ID is required.")
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Conversation not found.")
        
        if self.request.user not in conversation.participants.all():
            raise serializers.ValidationError("You are not part of this conversation.")
        
        serializer.save(sender=self.request.user, conversation=conversation)

