from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Message, Notification, MessageHistory


def home(request):
    """Home page view"""
    return render(request, 'messaging/home.html')


@login_required
def send_message(request):
    """Send a message to another user"""
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        content = request.POST.get('content')
        
        if receiver_username and content:
            try:
                receiver = User.objects.get(username=receiver_username)
                if receiver != request.user:
                    Message.objects.create(
                        sender=request.user,
                        receiver=receiver,
                        content=content
                    )
                    messages.success(request, f'Message sent to {receiver_username}!')
                else:
                    messages.error(request, 'You cannot send a message to yourself.')
            except User.DoesNotExist:
                messages.error(request, f'User {receiver_username} does not exist.')
        else:
            messages.error(request, 'Please provide both receiver and message content.')
    
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'messaging/send_message.html', {'users': users})


@login_required
def edit_message(request, message_id):
    """Edit a sent message"""
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    
    if request.method == 'POST':
        new_content = request.POST.get('content')
        edit_reason = request.POST.get('edit_reason', '')
        
        if new_content and new_content != message.content:
            # Update the message content (signal will handle history logging)
            message.content = new_content
            message.save()
            
            # Update the latest history entry with edit reason if provided
            if edit_reason:
                latest_history = MessageHistory.objects.filter(message=message).first()
                if latest_history:
                    latest_history.edit_reason = edit_reason
                    latest_history.save()
            
            messages.success(request, 'Message updated successfully!')
            return redirect('sent_messages')
        else:
            messages.error(request, 'Please provide new content to update the message.')
    
    return render(request, 'messaging/edit_message.html', {'message': message})


@login_required
def message_history(request, message_id):
    """View message edit history"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view this message history
    if request.user != message.sender and request.user != message.receiver:
        messages.error(request, 'You do not have permission to view this message history.')
        return redirect('home')
    
    history_list = MessageHistory.objects.filter(message=message).select_related('edited_by')
    paginator = Paginator(history_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'messaging/message_history.html', {
        'message': message,
        'page_obj': page_obj
    })


@login_required
def inbox(request):
    """View received messages"""
    messages_list = Message.objects.filter(receiver=request.user).select_related('sender')
    paginator = Paginator(messages_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'messaging/inbox.html', {'page_obj': page_obj})


@login_required
def sent_messages(request):
    """View sent messages"""
    messages_list = Message.objects.filter(sender=request.user).select_related('receiver')
    paginator = Paginator(messages_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'messaging/sent_messages.html', {'page_obj': page_obj})


@login_required
def notifications(request):
    """View notifications"""
    notifications_list = Notification.objects.filter(user=request.user)
    paginator = Paginator(notifications_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'messaging/notifications.html', {'page_obj': page_obj})


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications')