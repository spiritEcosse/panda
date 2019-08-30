from unittest import TestCase
from unittest.mock import patch, Mock, mock_open

from django.test.utils import override_settings

from .messages import Converter, receive_message

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
        self.converter = Converter(self.update)

    @override_settings(CHAT_ID=11)
    def test_wrong_chat_id_receive_message(self):
        assert receive_message(Mock(), self.update) is None

    @override_settings(CHAT_ID=10)
    def test_create_csv_file_products_receive_message(self):
        mo = mock_open()
        mock_valid_caption = Mock()
        file_name = "unique-string"
        mock_file_name = Mock(return_value=file_name)
        with patch('panda.telegram_bot.messages.open', mo):
            with patch('panda.telegram_bot.messages.Converter.valid_caption', mock_valid_caption):
                with patch('panda.telegram_bot.messages.Converter.file_name', mock_file_name):
                    assert receive_message(Mock(), self.update)

        mo.assert_called_once_with(file_name, 'w', newline='')
        mock_valid_caption.assert_called_once_with()
        mock_file_name.assert_called_once_with()

    def test_unique_file_name(self):
        string = "unique_string"
        mock_uuid = Mock(return_value=string)
        with patch('panda.telegram_bot.messages.uuid.uuid4', mock_uuid):
            assert self.converter.file_name() == "{}.csv".format(string)

        mock_uuid.assert_called_once_with()

    def test_caption_receive_message(self):
        for inp, exp in data_test_various_caption:
            self.update.channel_post.caption = inp
            converter = Converter(self.update)
            assert converter.valid_caption() == exp
