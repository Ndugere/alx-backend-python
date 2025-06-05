from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, creating, updating, and deleting conversations.
    Only authenticated participants can access their conversations.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        conversation = self.get_object()
        if conversation.created_by != request.user:
            return Response(
                {'detail': 'You are not authorized to delete this conversation!'},
                status=status.HTTP_403_FORBIDDEN
            )
        conversation.delete()
        return Response({'detail': 'Conversation deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, creating, updating, and deleting messages.
    Only authenticated users who are participants of a conversation can interact.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_pk')  # Assuming nested routing
        return Message.objects.filter(
            conversation__conversation_id=conversation_id,
            conversation__participants=self.request.user
        ).order_by('sent_at')

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_pk')
        try:
            conversation = Conversation.objects.get(
                conversation_id=conversation_id,
                participants=self.request.user
            )
        except Conversation.DoesNotExist:
            raise ValidationError("You are not a participant in this conversation.")
        serializer.save(sender=self.request.user, conversation=conversation)
