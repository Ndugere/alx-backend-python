from rest_framework import permissions
from .models import Conversation, Message

class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()

    def has_permission(self, request, view):
        # This is optional unless you want to check permission before get_object() is called
        return True
class IsMessageSender(permissions.BasePermission):
    """
    Custom permission to allow only the sender of a message to update/delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user
