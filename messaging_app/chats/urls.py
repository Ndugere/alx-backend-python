from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet, StatusViewSet

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'statuses', StatusViewSet, basename='status')  # Optional

urlpatterns = [
    path('', include(router.urls)),
]
