from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """
    Serialize user information with a custom display name.
    """
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'first_name',
            'last_name',
            'display_name',
            'email',
            'profile_picture',
            'bio',
            'phone_number',
            'is_online',
            'last_seen'
        ]
        read_only_fields = ['user_id', 'is_online', 'last_seen']

    def get_display_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username


class MessageSerializer(serializers.ModelSerializer):
    """
    Serialize a message, nesting sender details.
    """
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'conversation',
            'message_body',
            'sent_at',
            'is_read'
        ]
        read_only_fields = ['message_id', 'sender', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, required=False
    )
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'name',
            'participants',
            'participant_ids',
            'created_at',
            'messages',
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def create(self, validated_data):
        request_user = self.context['request'].user
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(
        created_by=request_user,
        **validated_data
    )
       
        conversation.participants.add(request_user, *participant_ids)
        return conversation

    def update(self, instance, validated_data):
        # Optional: Handle updates if needed, e.g., name or participants
        participant_ids = validated_data.pop('participant_ids', None)
        if participant_ids is not None:
            instance.participants.set(participant_ids + [self.context['request'].user])
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
