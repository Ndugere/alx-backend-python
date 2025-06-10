from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from .models import Message, Notification
from .signals import create_message_notification, create_welcome_notification


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
        # Count existing notifications
        initial_notification_count = Notification.objects.count()
        
        # Create a new message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, this is a test message!"
        )
        
        # Check that a notification was created
        self.assertEqual(
            Notification.objects.count(), 
            initial_notification_count + 1
        )
        
        # Check notification details
        notification = Notification.objects.filter(user=self.user2).last()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')
        self.assertIn(self.user1.username, notification.title)
        self.assertIn(message.content, notification.content)
        self.assertFalse(notification.is_read)

    def test_message_update_does_not_trigger_notification(self):
        """Test that updating a message doesn't create additional notifications"""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message"
        )
        
        # Count notifications after creation
        notification_count_after_create = Notification.objects.count()
        
        # Update the message
        message.content = "Updated message content"
        message.save()
        
        # Check that no additional notification was created
        self.assertEqual(
            Notification.objects.count(),
            notification_count_after_create
        )

    def test_welcome_notification_for_new_user(self):
        """Test that new users receive welcome notifications"""
        # Count existing notifications
        initial_count = Notification.objects.count()
        
        # Create a new user
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='testpass123'
        )
        
        # Check that a welcome notification was created
        self.assertEqual(
            Notification.objects.count(),
            initial_count + 1
        )
        
        # Check welcome notification details
        welcome_notification = Notification.objects.filter(
            user=new_user,
            notification_type='system'
        ).last()
        
        self.assertIsNotNone(welcome_notification)
        self.assertEqual(welcome_notification.user, new_user)
        self.assertEqual(welcome_notification.notification_type, 'system')
        self.assertIn('Welcome', welcome_notification.title)
        self.assertIn(new_user.username, welcome_notification.content)

    def test_signal_disconnection(self):
        """Test signal disconnection for testing purposes"""
        # Disconnect the signal
        post_save.disconnect(create_message_notification, sender=Message)
        
        # Count existing notifications
        initial_count = Notification.objects.count()
        
        # Create a message
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="This should not trigger a notification"
        )
        
        # Check that no notification was created
        self.assertEqual(Notification.objects.count(), initial_count)
        
        # Reconnect the signal for other tests
        post_save.connect(create_message_notification, sender=Message)

    def test_notification_str_method(self):
        """Test the string representation of Notification model"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message for string representation"
        )
        
        notification = Notification.objects.filter(user=self.user2).last()
        expected_str = f"Notification for {self.user2.username}: {notification.title}"
        self.assertEqual(str(notification), expected_str)

    def test_message_str_method(self):
        """Test the string representation of Message model"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="This is a test message for string representation"
        )
        
        expected_str = f"From {self.user1.username} to {self.user2.username}: This is a test message for string representation..."
        self.assertEqual(str(message), expected_str)

    def test_notification_mark_as_read_method(self):
        """Test the mark_as_read method of Notification model"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message for mark as read"
        )
        
        notification = Notification.objects.filter(user=self.user2).last()
        
        # Initially should be unread
        self.assertFalse(notification.is_read)
        
        # Mark as read
        notification.mark_as_read()
        
        # Should now be read
        self.assertTrue(notification.is_read)

    def test_long_message_content_truncation_in_notification(self):
        """Test that long message content is properly truncated in notifications"""
        long_content = "A" * 150  # Create a message longer than 100 characters
        
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content=long_content
        )
        
        notification = Notification.objects.filter(user=self.user2).last()
        
        # Check that notification content includes truncation
        self.assertIn('...', notification.content)
        self.assertTrue(len(notification.content) < len(long_content) + 50)  # Account for username and other text