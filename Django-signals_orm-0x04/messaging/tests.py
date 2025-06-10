from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.utils import timezone
from django.urls import reverse
from .models import Message, Notification, MessageHistory
from .signals import (
    create_message_notification, 
    create_welcome_notification, 
    log_message_edit,
    cleanup_user_related_data,
    log_user_deletion
)


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
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        initial_history_count = MessageHistory.objects.count()
        
        message.content = "Edited content"
        message.save()
        
        self.assertEqual(MessageHistory.objects.count(), initial_history_count + 1)
        
        history = MessageHistory.objects.filter(message=message).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.edited_by, self.user1)
        
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertIsNotNone(message.last_edited)

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


class UserDeletionSignalTest(TestCase):
    """Test cases for user deletion signals"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        # Create some test data
        self.message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message from user1 to user2"
        )
        
        self.message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message from user2 to user1"
        )
        
        # Edit a message to create history
        self.message1.content = "Edited message"
        self.message1.save()

    def test_user_deletion_removes_all_related_data(self):
        """Test that deleting a user removes all related data"""
        user1_id = self.user1.id
        
        # Count related data before deletion
        initial_messages = Message.objects.filter(
            models.Q(sender=self.user1) | models.Q(receiver=self.user1)
        ).count()
        initial_notifications = Notification.objects.filter(user=self.user1).count()
        initial_histories = MessageHistory.objects.filter(edited_by=self.user1).count()
        
        # Ensure we have some data
        self.assertGreater(initial_messages, 0)
        self.assertGreater(initial_notifications, 0)
        self.assertGreater(initial_histories, 0)
        
        # Delete the user
        self.user1.delete()
        
        # Check that all related data is gone
        remaining_messages = Message.objects.filter(
            models.Q(sender_id=user1_id) | models.Q(receiver_id=user1_id)
        ).count()
        remaining_notifications = Notification.objects.filter(user_id=user1_id).count()
        remaining_histories = MessageHistory.objects.filter(edited_by_id=user1_id).count()
        
        self.assertEqual(remaining_messages, 0)
        self.assertEqual(remaining_notifications, 0)
        self.assertEqual(remaining_histories, 0)

    def test_cascade_deletion_preserves_other_user_data(self):
        """Test that deleting one user doesn't affect other users' data"""
        # Count user2's data before user1 deletion
        user2_messages = Message.objects.filter(
            models.Q(sender=self.user2) | models.Q(receiver=self.user2)
        ).count()
        user2_notifications = Notification.objects.filter(user=self.user2).count()
        
        # Delete user1
        self.user1.delete()
        
        # Check that user2's data is still intact
        remaining_user2_messages = Message.objects.filter(
            models.Q(sender=self.user2) | models.Q(receiver=self.user2)
        ).count()
        remaining_user2_notifications = Notification.objects.filter(user=self.user2).count()
        
        # user2 should have lost messages involving user1, but keep others
        self.assertLessEqual(remaining_user2_messages, user2_messages)
        self.assertLessEqual(remaining_user2_notifications, user2_notifications)

    def test_signal_disconnection_for_user_deletion(self):
        """Test signal disconnection for user deletion"""
        # Disconnect the signals
        post_delete.disconnect(cleanup_user_related_data, sender=User)
        pre_delete.disconnect(log_user_deletion, sender=User)
        
        user_id = self.user1.id
        
        # Delete user (signals shouldn't fire)
        self.user1.delete()
        
        # Reconnect signals for other tests
        post_delete.connect(cleanup_user_related_data, sender=User)
        pre_delete.connect(log_user_deletion, sender=User)


class UserDeletionViewTest(TestCase):
    """Test cases for user deletion views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create some test data
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        Message.objects.create(
            sender=self.user,
            receiver=other_user,
            content="Test message"
        )

    def test_delete_account_view_requires_login(self):
        """Test that delete account view requires authentication"""
        response = self.client.get(reverse('delete_account'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_delete_account_get_shows_stats(self):
        """Test that GET request shows user statistics"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('delete_account'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'sent_messages')

    def test_delete_account_post_with_wrong_password(self):
        """Test account deletion with wrong password"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('delete_account'), {
            'password': 'wrongpassword',
            'confirmation': 'DELETE'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid password')
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_delete_account_post_with_wrong_confirmation(self):
        """Test account deletion with wrong confirmation"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('delete_account'), {
            'password': 'testpass123',
            'confirmation': 'delete'  # lowercase, should fail
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type "DELETE" exactly')
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_successful_account_deletion(self):
        """Test successful account deletion"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('delete_account'), {
            'password': 'testpass123',
            'confirmation': 'DELETE'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_user_profile_view(self):
        """Test user profile view shows statistics"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'sent_messages')
        self.assertContains(response, 'received_messages')