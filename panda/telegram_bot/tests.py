import csv
import datetime
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch, Mock, mock_open, MagicMock

import pytest
from django.test.utils import override_settings
from rest_framework import serializers

from panda.telegram_bot.serializers import MessageSerializer
from panda.telegram_bot.views import Converter

class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2019, 9, 5, 14, 47, 30, 538414)

datetime.datetime = MockDateTime

data_test_various_caption = (
    ("Наименование\nНа заказ\nЦена: 100$\nОписание\nКатегория>Подкатегория",
     {"title": "Наименование", "availability": "На заказ", "price_excl_tax": "Цена: 100$",
      "description": "Описание", "category_str": "Категория>Подкатегория"}),
    ("\n\nНаименование\n\nНа заказ\n\nЦена: 100$\n\nОписание\n\nКатегория\n",
     {"title": "Наименование", "availability": "На заказ", "price_excl_tax": "Цена: 100$",
      "description": "Описание", "category_str": "Категория"}),
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

data_test_various_availability = (
    ("В наличии", True),
    ("На заказ", False),
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

@pytest.mark.parametrize("inp,exp", data_test_various_availability)
def test_various_production_days(inp, exp):
    ms = MessageSerializer()
    assert ms.validate_availability(inp) == exp


class MessagesTest(TestCase):

    def setUp(self):
        self.request = Mock()
        self.request.data.channel_post.chat_id = 10
        self.converter = Converter()

    @override_settings(CHAT_ID=11)
    def test_wrong_chat_id(self):
        assert self.converter.run(self.request) is None

    def test_write(self):
        mo = mock_open()
        mock_csv_writer = MagicMock()
        serializer = MagicMock()
        validated_data = [1, 2]
        serializer.validated_data.values.return_value = validated_data
        file_name = "unique-string"
        self.converter.file_name = file_name

        with patch('panda.telegram_bot.views.open', mo):
            with patch('panda.telegram_bot.views.csv.writer', mock_csv_writer):
                self.converter.write(serializer)

        mo.assert_called_once_with(file_name, 'w', newline='')
        mock_csv_writer.assert_called_once_with(mo(), quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer = mock_csv_writer()
        csv_writer.writerow.assert_called_once_with(validated_data)

    @override_settings(CHAT_ID=10)
    def test_run(self):
        mock_serializer = MagicMock()
        mock_write = MagicMock()
        my_data = {"my": "data"}
        get_data = MagicMock(return_value=my_data)
        self.converter.write = mock_write
        self.converter.get_data = get_data
        self.converter.get_serializer = mock_serializer

        assert self.converter.run(self.request) is True

        get_data.assert_called_once_with()
        mock_serializer.assert_called_once_with(data=my_data)
        serializer = mock_serializer()
        serializer.is_valid.assert_called_once_with(raise_exception=True)
        mock_write.assert_called_once_with(serializer)

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
        mock_re = Mock(side_effect=serializers.ValidationError(message), return_value=None)

        with self.assertRaisesRegexp(serializers.ValidationError, message):
            with patch('panda.telegram_bot.serializers.re.match', mock_re):
                self.ms.validate_price_excl_tax(value)

        mock_re.assert_called_once_with(r".*:\s*(?P<price>\d+)(?P<hundredths>\.\d+)*(.*/.*)*", value)

    def test_we_make_wrong_price(self):
        value = "100didnotsee"
        message = "Wrong field price."
        mock_decimal = Mock(side_effect=serializers.ValidationError(message))

        with self.assertRaisesRegexp(serializers.ValidationError, message):
            with patch('panda.telegram_bot.serializers.Decimal', mock_decimal):
                self.ms.validate_price_excl_tax(value)

    def test_unique_upc(self):
        upc = 1567694850538414
        now = datetime.datetime.now()
        mock_datetime_now = Mock(return_value=now)

        with patch('panda.telegram_bot.serializers.datetime.datetime.now', mock_datetime_now):
            assert MessageSerializer().get_upc() == upc

        mock_datetime_now.assert_called_once_with()

    def test_required_fields(self):
        self.assertListEqual(
            ['title', "availability", 'price_excl_tax', 'description', "category_str"],
            [field for field, kw in self.ms.Meta.extra_kwargs.items() if kw['required']]
        )

    def test_order_fields(self):
        self.assertListEqual(
            ['title', "availability", 'price_excl_tax', 'description', "category_str",
             "production_days", "product_class", "upc"],
            self.ms.Meta.fields
        )
