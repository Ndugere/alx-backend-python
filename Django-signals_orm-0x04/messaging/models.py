from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Message(models.Model):
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    last_edited = models.DateTimeField(null=True, blank=True)
    
    # Self-referential foreign key for threaded conversations (replies)
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        edit_status = " (Edited)" if self.edited else ""
        reply_status = " (Reply)" if self.parent_message else ""
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}...{edit_status}{reply_status}"

    def mark_as_edited(self):
        """Mark message as edited and update timestamp"""
        self.edited = True
        self.last_edited = timezone.now()
        self.save()

    def is_reply(self):
        """Check if this message is a reply to another message"""
        return self.parent_message is not None

    def get_thread_messages(self):
        """Get all messages in the same thread (recursive)"""
        from django.db.models import Q
        
        if self.parent_message:
            # If this is a reply, get the root message's thread
            root_message = self.get_root_message()
            return Message.objects.filter(
                Q(id=root_message.id) | 
                Q(parent_message__in=root_message.get_all_descendants())
            ).order_by('timestamp')
        else:
            # If this is a root message, get all its descendants
            return Message.objects.filter(
                Q(id=self.id) | 
                Q(parent_message__in=self.get_all_descendants())
            ).order_by('timestamp')

    def get_root_message(self):
        """Get the root message of the thread"""
        if self.parent_message:
            return self.parent_message.get_root_message()
        return self

    def get_all_descendants(self):
        """Get all descendant messages (replies and their replies)"""
        descendants = list(self.replies.all())
        for reply in self.replies.all():
            descendants.extend(reply.get_all_descendants())
        return descendants

    def get_reply_count(self):
        """Get the total number of replies to this message"""
        return len(self.get_all_descendants())


class MessageHistory(models.Model):
    """Model to store message edit history"""
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_content = models.TextField()
    edited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_edits'
    )
    edited_at = models.DateTimeField(default=timezone.now)
    edit_reason = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-edited_at']
        verbose_name = 'Message History'
        verbose_name_plural = 'Message Histories'

    def __str__(self):
        return f"Edit history for message {self.message.id} by {self.edited_by.username}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('reply', 'New Reply'),
        ('system', 'System Notification'),
        ('edit', 'Message Edited'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='message'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()