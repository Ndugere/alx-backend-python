from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def notify_on_new_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(recipient=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def save_message_revision(sender, instance, **kwargs):
    if instance.pk:
        orig = Message.objects.get(pk=instance.pk)
        if orig.content != instance.content:
            MessageHistory.objects.create(message=instance, old_content=orig.content, edited_by=instance.sender)
            instance.edited = True

@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def cleanup_user_related(sender, instance, **kwargs):
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(recipient=instance).delete()
    MessageHistory.objects.filter(message__sender=instance).delete()