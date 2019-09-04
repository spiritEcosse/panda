from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch, Mock

import pytest
from django.test.utils import override_settings

from panda.telegram_bot.exceptions import MessageException
from panda.telegram_bot.serializers import MessageSerializer
from panda.telegram_bot.views import Converter


data_test_various_caption = (
    ("Наименование\nОписание\nЦена: 100$\nКатегория>Подкатегория",
     {"title": "Наименование", "description": "Описание", "price_excl_tax": "Цена: 100$",
      "category_str": "Категория>Подкатегория"}),
    ("\n\nНаименование\n\nОписание\nЦена: 100$\n\nКатегория\n",
     {"title": "Наименование", "description": "Описание", "price_excl_tax": "Цена: 100$",
      "category_str": "Категория"}),
)
data_test_various_price = (
    ("Цена: 100$", Decimal("100")),
    ("Price: 100$", Decimal("100")),
    ("Price: 100$/50€", Decimal("100")),
    ("Price:100$/50€", Decimal("100")),
    ("Price:100$ / 50€", Decimal("100")),
    ("Price:  100$  / 50€", Decimal("100")),
    ("Price:  100.90", Decimal("100.90")),
)

data_test_various_production_days = (
    ("Срок изготовления: 10 дней.", 10),
    ("Production days:10days.", 10),
)

data_test_various_category_str = (
    ("категория", "Категория"),
    ("категория > подкатегория", "Категория > Подкатегория"),
    ("Категория>Подкатегория", "Категория > Подкатегория"),
)

@pytest.mark.parametrize("inp,exp", data_test_various_price)
def test_validate_price_excl_tax(inp, exp):
    ms = MessageSerializer()
    assert ms.validate_price_excl_tax(inp) == exp

@pytest.mark.parametrize("inp,exp", data_test_various_category_str)
def test_validate_category_str(inp, exp):
    ms = MessageSerializer()
    assert ms.validate_category_str(inp) == exp

@pytest.mark.parametrize("inp,exp", data_test_various_caption)
def test_parse_caption(inp, exp):
    request = Mock()
    request.data.channel_post.caption = inp
    converter = Converter()
    converter.request = request
    assert converter.get_data() == exp

@pytest.mark.parametrize("inp,exp", data_test_various_production_days)
def test_various_production_days(inp, exp):
    ms = MessageSerializer()
    assert ms.validate_production_days(inp) == exp


class MessagesTest(TestCase):

    def setUp(self):
        self.request = Mock()
        self.request.data.channel_post.chat_id = 10
        self.converter = Converter()

    @override_settings(CHAT_ID=11)
    def test_wrong_chat_id(self):
        assert self.converter.run(self.request) is None

    # def test_write(self):
    #     mo = mock_open()
    #     mock_valid_caption = Mock()
    #     file_name = "unique-string"
    #     mock_file_name = Mock(return_value=file_name)
    #     with patch('panda.telegram_bot.views.open', mo):
    #         with patch('panda.telegram_bot.views.Converter.parse_caption', mock_valid_caption):
    #             with patch('panda.telegram_bot.views.Converter.file_name', mock_file_name):
    #                 assert receive_message(Mock(), self.update)
    #
    #     mo.assert_called_once_with(file_name, 'w', newline='')
    #     mock_valid_caption.assert_called_once_with()
    #     mock_file_name.assert_called_once_with()

    @override_settings(CHAT_ID=10)
    def test_run(self):
        serializer = Mock()
        my_data = {"my": "data"}
        get_data = Mock(return_value=my_data)
        with patch('panda.telegram_bot.views.Converter.get_serializer', serializer):
            with patch('panda.telegram_bot.views.Converter.get_data', get_data):
                assert self.converter.run(self.request)

        get_data.assert_called_once()
        serializer.assert_called_once_with(data=my_data)
        handle = serializer()
        handle.is_valid.assert_called_once_with(raise_exception=True)

    def test_unique_file_name(self):
        string = "unique_string"
        mock_uuid = Mock(return_value=string)
        with patch('panda.telegram_bot.views.uuid.uuid4', mock_uuid):
            assert Converter().file_name == "{}.csv".format(string)

        mock_uuid.assert_called_once_with()


class MessageSerializerTest(TestCase):

    def setUp(self):
        self.ms = MessageSerializer()

    def test_value_does_not_contain_price(self):
        value = "Wrong price."
        message = "Wrong field price."
        mock_re = Mock(side_effect=MessageException(message), return_value=None)

        with self.assertRaisesRegexp(MessageException, message):
            with patch('panda.telegram_bot.serializers.re.match', mock_re):
                self.ms.validate_price_excl_tax(value)

        mock_re.assert_called_once_with(r".*:\s*(?P<price>\d+)(?P<hundredths>\.\d+)*(.*/.*)*", value)

    def test_we_make_wrong_price(self):
        value = "100didnotsee"
        message = "Wrong field price."
        mock_decimal = Mock(side_effect=MessageException(message))

        with self.assertRaisesRegexp(MessageException, message):
            with patch('panda.telegram_bot.serializers.Decimal', mock_decimal):
                self.ms.validate_price_excl_tax(value)

