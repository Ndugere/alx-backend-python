from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

class SignalTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('u1', password='pw')
        self.u2 = User.objects.create_user('u2', password='pw')

    def test_notification_created(self):
        msg = Message.objects.create(sender=self.u1, receiver=self.u2, content="Hi")
        self.assertTrue(Notification.objects.filter(message=msg, recipient=self.u2).exists())

    def test_history_on_edit(self):
        msg = Message.objects.create(sender=self.u1, receiver=self.u2, content="Hi")
        msg.content = "Hello"
        msg.save()
        self.assertTrue(MessageHistory.objects.filter(message=msg, old_content="Hi").exists())