from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, StatusViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'statuses', StatusViewSet, basename='status')  # Optional: only if you're using status updates

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
