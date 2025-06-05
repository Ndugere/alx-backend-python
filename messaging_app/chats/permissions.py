from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to access or modify messages or conversations.
    """

    def has_object_permission(self, request, view, obj):
        # For Conversation objects
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()

        # For Message objects
        if isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()

        return False

    def has_permission(self, request, view):
        # Only allow access if user is authenticated
        return request.user and request.user.is_authenticated
