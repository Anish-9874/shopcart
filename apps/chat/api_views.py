from rest_framework.viewsets import ModelViewSet

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class ChatRoomViewSet(ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
