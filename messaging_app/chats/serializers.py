from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'bio', 'phone_number', 'is_online', 'last_seen']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True) 

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)  
    messages = MessageSerializer(many=True, read_only=True) 

    class Meta:
        model = Conversation
        fields = ['id', 'name', 'participants', 'created_at', 'messages']
