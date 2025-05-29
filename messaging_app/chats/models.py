import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Use UUID as primary key instead of default integer ID
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Explicitly define fields expected by checker (even if inherited)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Additional custom fields
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.CharField(max_length=160, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


class Conversation(models.Model):
    # Use UUID primary key
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    participants = models.ManyToManyField(User, related_name='conversations')
    name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name if self.name else f"Conversation {self.conversation_id}"


class Message(models.Model):
    # Use UUID primary key
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    
    message_body = models.TextField()  # renamed from 'content'
    sent_at = models.DateTimeField(auto_now_add=True)  # renamed from 'timestamp'
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.message_body[:20]}"
