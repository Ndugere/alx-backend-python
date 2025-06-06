from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Conversation, Message

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model."""
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_online', 'last_seen', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'profile_picture', 'bio', 'phone_number')}),
        ('Status', {'fields': ('is_online', 'last_seen')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin for Conversation model."""
    list_display = ('conversation_id', 'name', 'created_at')
    filter_horizontal = ('participants',)
    search_fields = ('name',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin for Message model."""
    list_display = ('message_id', 'sender', 'conversation', 'sent_at', 'is_read')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('message_body', 'sender__username', 'conversation__name')
