from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to access or modify the conversation and its messages.
    """

    def has_permission(self, request, view):
        # Only allow access to authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Handle conversation object
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()

        # Handle message object
        if isinstance(obj, Message):
            # PUT, PATCH, DELETE only allowed if sender is the user
            if request.method in ["PUT", "PATCH", "DELETE"]:
                return obj.sender == request.user
            return request.user in obj.conversation.participants.all()

        return False
