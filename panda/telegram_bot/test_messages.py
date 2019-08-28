from unittest.mock import patch, Mock, mock_open
from .messages import receive_message, Updater, valid_caption
from django.test import TestCase
from django.test.utils import override_settings
import pytest

data_test_various_caption = (
    ("\n\nтест\nтест\nтест\nтест\n", ["тест", "тест", "тест", "тест"]),
    ("тест\nтест\nтест\nтест\n", ["тест", "тест", "тест", "тест"]),
    ("\nтест\nтест\nтест\nтест\n", ["тест", "тест", "тест", "тест"]),
    ("тест\nтест\nтест\nтест", ["тест", "тест", "тест", "тест"]),
    ("тест\n\n\nтест\nтест\n\nтест", ["тест", "тест", "тест", "тест"]),
)


class MessagesTest(TestCase):

    def setUp(self):
        self.update = Mock()
        self.update.channel_post.chat_id = 10
        self.update.channel_post.caption = ""

    @override_settings(CHAT_ID=11)
    def test_wrong_chat_id_receive_message(self):
        assert receive_message(Mock(), self.update) is None

    @override_settings(CHAT_ID=10)
    def test_create_csv_file_products_receive_message(self):
        mo = mock_open()
        mock_valid_caption = Mock()
        with patch('panda.telegram_bot.messages.open', mo):
            with patch('panda.telegram_bot.messages.valid_caption', mock_valid_caption):
                assert receive_message(Mock(), self.update)

        mo.assert_called_once_with('product.csv', 'w', newline='')
        mock_valid_caption.assert_called_once_with("")


@pytest.mark.parametrize("inp,exp", data_test_various_caption)
def test_caption_receive_message(inp, exp):
    assert valid_caption(inp) == exp
