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
    ("title\navailability\nPrice: 100$\ndescription\ncategory_str>category_str",
     {"title": "title", "availability": "availability", "price_excl_tax": "Price: 100$",
      "description": "description", "category_str": "category_str>category_str"}),
    ("\n\n\r\ttitle\n\r\navailability\n\rPrice: 100$\n\t\rdescription\n\rcategory_str>category_str",
     {"title": "title", "availability": "availability", "price_excl_tax": "Price: 100$",
      "description": "description", "category_str": "category_str>category_str"}),
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

@pytest.mark.unit
@pytest.mark.parametrize("inp,exp", data_test_various_price)
def test_parse_price_excl_tax(inp, exp):
    ms = MessageSerializer()
    assert ms.parse_price_excl_tax(inp) == exp

@pytest.mark.unit
@pytest.mark.parametrize("inp,exp", data_test_various_category_str)
def test_parse_category_str(inp, exp):
    ms = MessageSerializer()
    assert ms.parse_category_str(inp) == exp

@pytest.mark.unit
@pytest.mark.parametrize("inp,exp", data_test_various_caption)
def test_validate_caption(inp, exp):
    update = Mock()
    update.channel_post.caption = inp
    converter = Converter()
    assert converter.get_data(update) == exp

@pytest.mark.unit
@pytest.mark.parametrize("inp,exp", data_test_various_production_days)
def test_various_production_days(inp, exp):
    ms = MessageSerializer()
    assert ms.parse_production_days(inp) == exp

@pytest.mark.unit
@pytest.mark.parametrize("inp,exp", data_test_various_availability)
def test_various_production_days(inp, exp):
    ms = MessageSerializer()
    assert ms.parse_availability(inp) == exp


@pytest.mark.unit
class MessagesTest(TestCase):

    def setUp(self):
        self.converter = Converter()

    @override_settings(CHAT_ID=11)
    @override_settings(TOKEN_TELEGRAM="some")
    def test_wrong_chat_id(self):
        request, update, response, status, settings, bot, loads = \
            Mock(), Mock(), Mock(), Mock(), Mock(), Mock(), Mock()
        update.channel_post.chat_id = 10
        status.HTTP_500_INTERNAL_SERVER_ERROR = 500
        request.body = "json"
        update = Mock(return_value=update)

        with patch('panda.telegram_bot.views.Bot', bot):
            with patch('panda.telegram_bot.views.Update.de_json', update):
                with patch('panda.telegram_bot.views.json.loads', loads):
                    with patch('panda.telegram_bot.views.Response', response):
                        self.converter.create(request)

        bot.assert_called_once_with("some")
        loads.assert_called_once_with(request.body)
        update.assert_called_once_with(loads(), bot())
        response.assert_called_once_with(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    def test_create(self):
        my_data = {"my": "data"}
        loads, bot, serializer, update, request, write, get_data, status, response = \
            Mock(), Mock(), Mock(), Mock(), Mock(), Mock(), MagicMock(return_value=my_data),\
            Mock(), Mock()
        update.channel_post.chat_id = 10
        status.HTTP_201_CREATED = 201
        self.converter.write = write
        self.converter.get_data = get_data
        self.converter.get_serializer = serializer
        update = Mock(return_value=update)

        with patch('panda.telegram_bot.views.Bot', bot):
            with patch('panda.telegram_bot.views.json.loads', loads):
                with patch('panda.telegram_bot.views.Update.de_json', update):
                    with patch('panda.telegram_bot.views.Response', response):
                        self.converter.create(request)

        get_data.assert_called_once_with(update())
        serializer.assert_called_once_with(data=my_data)
        serializer = serializer()
        serializer.is_valid.assert_called_once_with(raise_exception=True)
        write.assert_called_once_with(serializer)
        response.assert_called_once_with(status=status.HTTP_201_CREATED)

    def test_unique_file_name(self):
        string = "unique_string"
        mock_uuid = Mock(return_value=string)
        with patch('panda.telegram_bot.views.uuid.uuid4', mock_uuid):
            assert Converter().file_name == "{}.csv".format(string)

        mock_uuid.assert_called_once_with()


@pytest.mark.unit
class MessageSerializerTest(TestCase):

    def setUp(self):
        self.ms = MessageSerializer()

    def test_value_does_not_contain_price(self):
        value = "Wrong price."
        message = "Wrong field price."
        mock_re = Mock(side_effect=serializers.ValidationError(message), return_value=None)

        with self.assertRaisesRegexp(serializers.ValidationError, message):
            with patch('panda.telegram_bot.serializers.re.match', mock_re):
                self.ms.parse_price_excl_tax(value)

        mock_re.assert_called_once_with(r".*:\s*(?P<price>\d+)(?P<hundredths>\.\d+)*(.*/.*)*", value)

    def test_we_make_wrong_price(self):
        value = "100didnotsee"
        message = "Wrong field price."
        mock_decimal = Mock(side_effect=serializers.ValidationError(message))

        with patch('panda.telegram_bot.serializers.Decimal', mock_decimal):
            self.assertEqual(self.ms.parse_price_excl_tax(value), "")

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
