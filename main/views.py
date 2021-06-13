from main.models import Message
from main.serializers import CreateMessageSerializer, GetMessageSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action


class MessageView(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', ]

    def get_serializer_class(self):
        if self.action in ('create',):
            return CreateMessageSerializer
        return GetMessageSerializer

    def get_queryset(self):
        """
            Return the corresponding queryset (according to the action) ordered by the creation time
        """
        user = self.request.user
        queryset = (Message.objects.filter(reciever=user).filter(deleted_by_reciever=False) |
                    Message.objects.filter(sender=user).filter(deleted_by_sender=False))
        if self.action in ('list', 'unread', 'delete_inbox_message'):
            queryset = queryset.filter(reciever=user).filter(deleted_by_reciever=False)
            if self.action in ('unread', ):
                queryset = queryset.filter(is_read=False)
        if self.action in ('delete_outbox_message', ):
            queryset = queryset.filter(sender=user).filter(deleted_by_sender=False)
        return queryset.order_by('-created_at')

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
        """
            Returns a single message (optional from both inbox or outbox) according to the pk argument,
            if the user ask for income message, and its marked as'unread'
            then update is_read flag to true.
        """
        user = request.user
        try:
            message = self.get_queryset().get(id=pk)
        except Message.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if message.reciever.id == user.id and not message.is_read:
            message.is_read = True
            message.save()
        serializer = GetMessageSerializer(message)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        queryset = self.get_queryset()
        serializer = GetMessageSerializer(queryset, many=True)
        return Response(serializer.data)

    """
        Delete message section - each function mark the 'delete_by_sender/reciever' flag to true
        if the message was marked as deleted also in the other side
        then it will deleted from the database too.
    """

    @action(detail=True, methods=['delete'])
    def delete_inbox_message(self, request, pk):
        try:
            message = self.get_queryset().get(id=pk)
        except Message.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        message.deleted_by_reciever = True
        message.save()
        if message.deleted_by_sender:
            message.delete()
        return Response({"detail": "Message deleted successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def delete_outbox_message(self, request, pk):
        try:
            message = self.get_queryset().get(id=pk)
        except Message.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        message.deleted_by_sender = True
        message.save()
        if message.deleted_by_reciever:
            message.delete()
        return Response({"detail": "Message deleted successfully"}, status=status.HTTP_200_OK)




