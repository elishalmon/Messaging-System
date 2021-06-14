from main.views import MessageView
from django.urls import path

messages_list = MessageView.as_view({
    'get': 'list',
    #'get': 'unread',
})

unread_messages = MessageView.as_view({'get': 'unread'})

create_message = MessageView.as_view({
    'post': 'create',
})

get_message = MessageView.as_view({
    'get': 'retrieve',
})


delete_outbox_message = MessageView.as_view({
    'delete': 'delete_outbox_message',
})

delete_inbox_message = MessageView.as_view({
    'delete': 'delete_inbox_message',
})

urlpatterns = (
    path('', messages_list, name='messages'),
    path('unread/', unread_messages, name='messages-unread'),
    path('create/', create_message, name='messages-create'),
    path('<int:pk>/', get_message, name='read-message'),
    path('delete/inbox/<int:pk>/', delete_inbox_message, name='delete-inbox-message'),
    path('delete/outbox/<int:pk>/', delete_outbox_message, name='delete-outbox-message'),
)



