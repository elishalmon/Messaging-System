from rest_framework import serializers
from .models import Message
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', )


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('reciever', 'subject', 'body', )


class GetMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(many=False)
    reciever = UserSerializer(many=False)
    class Meta:
        model = Message
        fields = ('id', 'sender', 'reciever', 'subject', 'body', 'created_at', 'is_read', 'deleted_by_sender',
                  'deleted_by_reciever', )