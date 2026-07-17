from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'messages', api_views.MessageViewSet, basename='message')
router.register(r'chat-rooms', api_views.ChatRoomViewSet, basename='chat-room')

urlpatterns = router.urls