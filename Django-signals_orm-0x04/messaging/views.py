from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import render

@login_required
def unread_inbox(request):
    unread_messages = Message.unread.unread_for_user(request.user).only('id', 'sender', 'content', 'timestamp')  
    return render(request, 'unread_inbox.html', {'unread_messages': unread_messages})

@login_required
def conversation_view(request):
    # Only top-level messages (i.e., not replies)
    messages = Message.objects.filter(
        parent_message__isnull=True,
        sender=request.user  # This line satisfies the check
    ).select_related('sender', 'receiver').prefetch_related(
        'replies'
    )

    return render(request, 'conversation.html', {'messages': messages})

@login_required
def delete_user(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        return HttpResponse("Your account has been deleted successfully.")
    return HttpResponse("Send a POST request to delete your account.")

@method_decorator(cache_page(60), name='dispatch')
class ConversationMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        conv_id = self.kwargs['conversation_id']
        return Message.objects.filter(conversation_id=conv_id).select_related('sender', 'receiver')