from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test.utils import override_settings


class AccountTests(APITestCase):

    @override_settings(CHAT_ID=10)
    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse("some-list")
        data = {"update_id": 552201929, "channel_post": {"message_id": 78, "date": 1567772991, "chat": {"id": 10, "type": "channel", "title": "test_channel", "username": "test_channellllllllll"}, "entities": [], "caption_entities": [], "photo": [{"file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgQ", "width": 320, "height": 90, "file_size": 9260}, {"file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA3gAA87mAgABFgQ", "width": 800, "height": 225, "file_size": 46171}, {"file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA3kAA8_mAgABFgQ", "width": 1280, "height": 360, "file_size": 104567}], "caption": "Наименование\nНа заказ\nЦена: 100$\nОписание\nКатегория>Подкатегория", "new_chat_members": [], "new_chat_photo": [], "delete_chat_photo": False, "group_chat_created": False, "supergroup_chat_created": False, "channel_chat_created": False}, "_effective_message": {"message_id": 78, "date": 1567772991, "chat": {"id": -1001241134985, "type": "channel", "title": "test_channel", "username": "test_channellllllllll"}, "entities": [], "caption_entities": [], "photo": [{"file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgQ", "width": 320, "height": 90, "file_size": 9260}, {"file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA3gAA87mAgABFgQ", "width": 800, "height": 225, "file_size": 46171}, {"file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA3kAA8_mAgABFgQ", "width": 1280, "height": 360, "file_size": 104567}], "caption": "Кукла лисичка\n\nТип работы: в наличии, на заказ, для примера\n\nЦена-1000грн/300$\n\nОписание  Описание  Описание  Описание  Описание  Описание  Описание  Описание  Описание  Описание  Описание  Описание", "new_chat_members": [], "new_chat_photo": [], "delete_chat_photo": False, "group_chat_created": False, "supergroup_chat_created": False, "channel_chat_created": False}}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
