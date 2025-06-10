from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from .models import Message, Notification, MessageHistory
from .signals import create_message_notification, create_welcome_notification, log_message_edit


class MessageSignalTest(TestCase):
    """Test cases for message notification signals"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='testpass123'
        )

    def test_message_creation_triggers_notification(self):
        """Test that creating a message triggers a notification"""
        initial_notification_count = Notification.objects.count()
        
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, this is a test message!"
        )
        
        self.assertEqual(
            Notification.objects.count(), 
            initial_notification_count + 1
        )
        
        notification = Notification.objects.filter(user=self.user2).last()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')

    def test_message_edit_creates_history(self):
        """Test that editing a message creates a history record"""
        # Create original message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        initial_history_count = MessageHistory.objects.count()
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # Check that history was created
        self.assertEqual(MessageHistory.objects.count(), initial_history_count + 1)
        
        # Check history details
        history = MessageHistory.objects.filter(message=message).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.edited_by, self.user1)
        
        # Check that message is marked as edited
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertIsNotNone(message.last_edited)

    def test_message_edit_creates_notification(self):
        """Test that editing a message creates an edit notification"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # Clear existing notifications
        Notification.objects.filter(user=self.user2).delete()
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # Check for edit notification
        edit_notification = Notification.objects.filter(
            user=self.user2,
            notification_type='edit'
        ).first()
        
        self.assertIsNotNone(edit_notification)
        self.assertEqual(edit_notification.message, message)
        self.assertIn('edited', edit_notification.title.lower())

    def test_no_history_for_unchanged_content(self):
        """Test that saving without content change doesn't create history"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Same content"
        )
        
        initial_history_count = MessageHistory.objects.count()
        
        # Save without changing content
        message.is_read = True
        message.save()
        
        # No new history should be created
        self.assertEqual(MessageHistory.objects.count(), initial_history_count)
        self.assertFalse(message.edited)

    def test_multiple_edits_create_multiple_history_records(self):
        """Test that multiple edits create multiple history records"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Version 1"
        )
        
        # First edit
        message.content = "Version 2"
        message.save()
        
        # Second edit
        message.content = "Version 3"
        message.save()
        
        # Should have 2 history records
        history_count = MessageHistory.objects.filter(message=message).count()
        self.assertEqual(history_count, 2)
        
        # Check history order (latest first)
        histories = list(MessageHistory.objects.filter(message=message).order_by('-edited_at'))
        self.assertEqual(histories[0].old_content, "Version 2")  # Most recent edit
        self.assertEqual(histories[1].old_content, "Version 1")  # First edit

    def test_message_history_str_method(self):
        """Test the string representation of MessageHistory model"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original"
        )
        
        message.content = "Edited"
        message.save()
        
        history = MessageHistory.objects.filter(message=message).first()
        expected_str = f"Edit history for message {message.id} by {self.user1.username}"
        self.assertEqual(str(history), expected_str)

    def test_signal_disconnection_for_edit_logging(self):
        """Test signal disconnection for edit logging"""
        # Disconnect the pre_save signal
        pre_save.disconnect(log_message_edit, sender=Message)
        
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original"
        )
        
        initial_history_count = MessageHistory.objects.count()
        
        # Edit message
        message.content = "Edited without logging"
        message.save()
        
        # No history should be created
        self.assertEqual(MessageHistory.objects.count(), initial_history_count)
        
        # Reconnect the signal
        pre_save.connect(log_message_edit, sender=Message)

    def test_welcome_notification_for_new_user(self):
        """Test that new users receive welcome notifications"""
        initial_count = Notification.objects.count()
        
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='testpass123'
        )
        
        self.assertEqual(Notification.objects.count(), initial_count + 1)
        
        welcome_notification = Notification.objects.filter(
            user=new_user,
            notification_type='system'
        ).last()
        
        self.assertIsNotNone(welcome_notification)
        self.assertIn('Welcome', welcome_notification.title)