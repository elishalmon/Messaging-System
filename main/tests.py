from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Message
from django.urls import reverse


class TestMessagesApi(APITestCase):

    def setUp(self):
        auth_url = reverse('token_obtain_pair')
        self.user1 = User.objects.create_user(id=1, username='test1', password='12345678', email='test1@test1.com')
        self.user2 = User.objects.create_user(id=2, username='test2', password='12345678', email='test2@test2.com')

        response = self.client.post(auth_url, {'username': 'test1', 'password': '12345678'})
        self.jwt1 = response.data['access']
        response = self.client.post(auth_url, {'username': 'test2', 'password': '12345678'})
        self.jwt2 = response.data['access']

        self.message1 = Message.objects.create(id='1', sender=self.user1, reciever=self.user2, subject='test subject',
                                          body='test body')
        self.message2 = Message.objects.create(id='2', sender=self.user2, reciever=self.user1, subject='test subject',
                                          body='test body')
        self.message3 = Message.objects.create(id='3', sender=self.user2, reciever=self.user1, subject='test subject',
                                               body='test body')

    def test_send_request_without_jwt(self):
        url = reverse('messages')
        response = self.client.get(url)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    def test_send_request_with_wrong_jwt(self):
        url = reverse('messages')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.jwt1 + 't'))
        response = self.client.get(url)
        self.assertEqual(response.data, {"detail": "Given token not valid for any token type",
                                         "code": "token_not_valid",
                                         "messages": [{
                                            "token_class": "AccessToken",
                                            "token_type": "access",
                                            "message": "Token is invalid or expired"
                                            }]
                                         })

    def test_create_message(self):
        url = reverse('messages-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.jwt1))
        response = self.client.post(url, {'reciever': '2', 'subject': 'test subject', 'body': 'test body'})
        self.assertEqual(response.data['sender']['id'], self.user1.id)

    def test_create_message_missing_subject(self):
        url = reverse('messages-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.jwt1))
        response = self.client.post(url, {'reciever': '2', 'body': 'test body'})
        self.assertEqual(response.data, {"subject": ["This field is required."]})

    def test_get_message(self):
        url = reverse('read-message', args=[self.message1.id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.jwt1))
        response = self.client.get(url)
        self.assertEqual(response.data['id'], self.message1.id)

    def test_get_messages(self):
        url = reverse('messages')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.jwt1))
        response = self.client.get(url)
        assert(response.status_code == 200)

    def test_get_unread_messages(self):
        url = reverse('messages-unread')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.jwt1))
        response = self.client.get(url)
        assert(response.data[0]['is_read'] == False and response.data[1]['is_read'] == False)

    def test_delete_outbox_message(self):
        url = reverse('delete-outbox-message', args=[self.message1.id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.jwt1))
        self.client.delete(url)
        assert(Message.objects.filter(id=self.message1.id)[0].deleted_by_sender == True)

    def test_delete_inbox_message(self):
        url = reverse('delete-inbox-message', args=[self.message1.id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.jwt2))
        response = self.client.delete(url)
        self.assertEqual(response.data, {'detail': 'Message deleted successfully'})














