from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message, Notification, MessageHistory
import logging

# Set up logging
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal handler that logs message content before it's edited.
    
    This signal fires before a Message is saved, allowing us to capture
    the old content and store it in MessageHistory.
    """
    if instance.pk:  # Only for existing messages (updates)
        try:
            # Get the original message from database
            original_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has actually changed
            if original_message.content != instance.content:
                # Create history record with old content
                MessageHistory.objects.create(
                    message=original_message,
                    old_content=original_message.content,
                    edited_by=instance.sender,  # Assuming sender is editing
                    edited_at=timezone.now()
                )
                
                # Mark message as edited
                instance.edited = True
                instance.last_edited = timezone.now()
                
                logger.info(
                    f'Message edit logged for message {instance.pk} by {instance.sender.username}'
                )
                
        except Message.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            logger.warning(f'Attempted to log edit for non-existent message {instance.pk}')
        except Exception as e:
            logger.error(f'Error logging message edit: {str(e)}')


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a new message is created
    or when a message is edited.
    """
    if created:  # New message
        try:
            # Create notification for the receiver
            Notification.objects.create(
                user=instance.receiver,
                message=instance,
                notification_type='message',
                title=f'New message from {instance.sender.username}',
                content=f'{instance.sender.username} sent you a message: "{instance.content[:100]}..."'
                if len(instance.content) > 100 
                else f'{instance.sender.username} sent you a message: "{instance.content}"'
            )
            
            logger.info(
                f'Notification created for {instance.receiver.username} '
                f'about message from {instance.sender.username}'
            )
            
        except Exception as e:
            logger.error(f'Error creating notification: {str(e)}')
    
    elif instance.edited:  # Message was edited
        try:
            # Create notification for the receiver about the edit
            Notification.objects.create(
                user=instance.receiver,
                message=instance,
                notification_type='edit',
                title=f'Message edited by {instance.sender.username}',
                content=f'{instance.sender.username} edited their message to you.'
            )
            
            logger.info(
                f'Edit notification created for {instance.receiver.username} '
                f'about message edit by {instance.sender.username}'
            )
            
        except Exception as e:
            logger.error(f'Error creating edit notification: {str(e)}')


@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    """
    Create a welcome notification for new users.
    """
    if created:
        try:
            Notification.objects.create(
                user=instance,
                notification_type='system',
                title='Welcome to our messaging platform!',
                content=f'Hello {instance.username}, welcome to our platform! You can now send and receive messages.'
            )
            
            logger.info(f'Welcome notification created for new user: {instance.username}')
            
        except Exception as e:
            logger.error(f'Error creating welcome notification: {str(e)}')