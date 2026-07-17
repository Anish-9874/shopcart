from rest_framework import serializers
from .models import Message, ChatRoom


class ChatRoomSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ChatRoom
        fields = "__all__"



class MessageSerializer(serializers.ModelSerializer):
    room = serializers.StringRelatedField(read_only=True)
    sender = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Message
        fields = "__all__"