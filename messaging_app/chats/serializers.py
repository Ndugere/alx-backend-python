from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    # Example of SerializerMethodField: return full name or username
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'profile_picture', 'bio', 'phone_number', 'is_online', 'last_seen']

    def get_display_name(self, obj):
        # Returns first and last name if available else username
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    content = serializers.CharField(max_length=500)  # explicit CharField

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']

    def validate_content(self, value):
        # Raise validation error if message content is empty or too short
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Message content cannot be empty.")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'name', 'participants', 'created_at', 'messages']
