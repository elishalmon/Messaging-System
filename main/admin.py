from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'sender', 'reciever', )
    search_fields = ('subject', 'sender__username', 'reciever__username', )
    readonly_fields = ('created_at', )
