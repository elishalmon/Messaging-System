from main.models import Message
from main.serializers import CreateMessageSerializer, GetMessageSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action


class MessageView(viewsets.ModelViewSet):

    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action in ('create', ):
            return CreateMessageSerializer
        return GetMessageSerializer

    def get_queryset(self):
        user = self.request.user
        if self.action in ('list', ):
            return Message.objects.filter(reciever=user).filter(deleted_by_reciever=False)
        if self.action in ('unread', ):
            return Message.objects.filter(reciever=user).filter(deleted_by_reciever=False).filter(is_read=False)

    def create(self, request):
        serializer = CreateMessageSerializer(data=request.data)
        if serializer.is_valid():
            new_message = Message.objects.create(
                sender=request.user,
                reciever=serializer.validated_data['reciever'],
                subject=serializer.validated_data['subject'],
                body=serializer.validated_data['body'],
                is_read=False,
                deleted_by_sender=False,
                deleted_by_reciever=False,
            )
            new_message.save()
            serializer = GetMessageSerializer(new_message)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        user = request.user
        try:
            message = (Message.objects.filter(reciever=user).filter(deleted_by_reciever=False) |
                       Message.objects.filter(sender=user).filter(deleted_by_sender=False)).get(id=pk)
        except Message.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if message.reciever.id == user.id and not message.is_read:
            message.is_read = True
            message.save()
        serializer = GetMessageSerializer(message)
        return Response(serializer.data)

    @action(detail=False)
    def unread(self, request):
        queryset = self.get_queryset()
        serializer = GetMessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk):
        user = request.user
        try:
            message = (Message.objects.filter(reciever=user).filter(deleted_by_reciever=False) |
                Message.objects.filter(sender=user).filter(deleted_by_sender=False)).get(id=pk)
        except Message.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.id == message.reciever.id:
            message.deleted_by_reciever = True
            message.save()
            if message.deleted_by_sender:
                message.delete()
        else:
            message.deleted_by_sender = True
            message.save()
            if message.deleted_by_reciever:
                message.delete()
        return Response({"detail": "Message deleted successfully"}, status=status.HTTP_200_OK)
