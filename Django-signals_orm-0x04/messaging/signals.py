from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification
import logging

# Set up logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a new message is created.
    
    Args:
        sender: The model class that sent the signal (Message)
        instance: The actual instance being saved (Message instance)
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created:  # Only create notification for new messages
        try:
            # Create notification for the receiver
            notification = Notification.objects.create(
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


@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    """
    Optional: Create a welcome notification for new users.
    
    Args:
        sender: The model class that sent the signal (User)
        instance: The actual instance being saved (User instance)
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
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