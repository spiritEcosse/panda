from freezegun import freeze_time
import datetime
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock, call

import pytest
from django.test.utils import override_settings

from panda.telegram_bot.serializers import MessageSerializer, StockRecordSerializer, \
    ProductClassSerializer, PartnerSerializer, ProductImageSerializer
from panda.telegram_bot.views import Converter

data_test_various_caption = (
    ("title\n\navailability\n\nPrice: 100$\n\ndescription\ndescription\ndescription\n\ncategory_str>sub_category_str\n\nproduction days: 10 days.",
     {"title": "title", "availability": "availability", "stock": "Price: 100$",
      "description": "description\ndescription\ndescription", "category_str": "category_str>sub_category_str",
      "production_days": "production days: 10 days.", "image": "some"}),
    ("title\n\navailability\n\nPrice: 100$\n\ndescription\ndescription\ndescription\n\ncategory_str>sub_category_str",
     {"title": "title", "availability": "availability", "stock": "Price: 100$",
      "description": "description\ndescription\ndescription", "category_str": "category_str>sub_category_str",
      "image": "some"}),
    ("\n\n\r\ttitle\n\navailability\n\n\rPrice: 100$\n\n\t\rdescription\n\n\rcategory_str>category_str",
     {"title": "title", "availability": "availability", "stock": "Price: 100$",
      "description": "description", "category_str": "category_str>category_str", "image": "some"}),
)

data_test_various_price = (
    ("Цена: 100$", "100"),
    ("Price: 100$", "100"),
    ("Price: 100$/50€", "100"),
    ("Price:100$/50€", "100"),
    ("Price:100$ / 50€", "100"),
    ("Price:  100$  / 50€", "100"),
    ("Price:  100.90", "100.90"),
    ("Price-100.90", "100.90"),
    ("Wrong price.", ""),
)

data_test_various_production_days = (
    ("Срок изготовления: 10 дней.", 10),
    ("Production days:10days.", 10),
    ("no number visible", None),
)

data_test_various_category_str = (
    ("category", "Category"),
    ("category >category", "Category > Category"),
    ("Category>Category", "Category > Category"),
)

data_test_various_availability = (
    ("В наличии", True),
    ("На заказ", True),
)

data_test_various_num_in_stock = {
    (True, 1),
    (False, 0),
}

data_test_initial_parner_name = {
    ("Category > subcategory", "Category partner"),
    ("Category>subcategory", "Category partner"),
    ("category>subcategory", "Category partner"),
    ("Category", "Category partner"),
}

data_test_various_validate = (
    ({'stock': {"stock": "100"}, "availability": False}, {'stock': {'stock': "100", "num_in_stock": 0}, "availability": False}),
    ({'stock': {"stock": "100"}, "availability": True}, {'stock': {'stock': "100"}, "availability": True})
)

@pytest.mark.unit
@pytest.mark.parametrize("inp,exp", data_test_various_price)
def test_parse_stock(inp, exp):
    ms = StockRecordSerializer()
    assert ms.parse_price_excl_tax(Mock(), inp) == exp

@pytest.mark.unit
@pytest.mark.parametrize("inp, exp", data_test_various_category_str)
def test_parse_category_str(inp, exp):
    ms = MessageSerializer()
    assert ms.parse_category_str(Mock(), inp) == exp

@pytest.mark.unit
@pytest.mark.parametrize("inp, exp", data_test_various_caption)
def test_validate_caption(inp, exp):
    update = Mock()
    update.channel_post.caption = inp
    file_ = Mock()
    file_.get_file.return_value= "some"
    update.channel_post.photo = [file_]
    converter = Converter()
    assert converter.get_data(update) == exp

@pytest.mark.unit
@pytest.mark.parametrize("inp, exp", data_test_various_production_days)
def test_various_production_days(inp, exp):
    ms = MessageSerializer()
    assert ms.parse_production_days(Mock(), inp) == exp

@pytest.mark.unit
@pytest.mark.parametrize("inp, exp", data_test_various_availability)
def test_availability(inp, exp):
    ms = MessageSerializer()
    field = Mock()
    field.field_name = "availability"
    assert ms.parse_availability(field, inp) == exp
    assert ms.parsed_data == {field.field_name: exp}

@pytest.mark.unit
@pytest.mark.parametrize("inp, exp", data_test_various_num_in_stock)
def test_various_initial_num_in_stock(inp, exp):
    sr = StockRecordSerializer()
    sr.parsed_data = {"availability": inp}
    assert sr.initial_num_in_stock(Mock()) == exp


@pytest.mark.unit
@pytest.mark.parametrize("inp, exp", data_test_various_validate)
def test_validate(inp, exp):
    ms = MessageSerializer()
    # assert exp == ms.validate(inp)


@pytest.mark.unit
@pytest.mark.parametrize("inp, exp", data_test_initial_parner_name)
def test_partner_name(inp, exp):
    ps = PartnerSerializer()
    ps.parsed_data['category_str'] = inp
    assert ps.initial_name() == exp


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

    # def test_write(self):
    #     mo = mock_open()
    #     mock_csv_writer = MagicMock()
    #     serializer = MagicMock()
    #     validated_data = [1, 2]
    #     serializer.validated_data.values.return_value = validated_data
    #     file_name = "unique-string"
    #     self.converter.file_name = file_name
    #
    #     with patch('panda.telegram_bot.views.open', mo):
    #         with patch('panda.telegram_bot.views.csv.writer', mock_csv_writer):
    #             self.converter.write(serializer)
    #
    #     mo.assert_called_once_with(file_name, 'w', newline='')
    #     mock_csv_writer.assert_called_once_with(mo(), quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     csv_writer = mock_csv_writer()
    #     csv_writer.writerow.assert_called_once_with(validated_data)

    def test_create(self):
        my_data = {"my": "data"}
        loads, bot, serializer, update, request, get_data, status, response = \
            Mock(), Mock(), Mock(), Mock(), Mock(), MagicMock(return_value=my_data),\
            Mock(), Mock()
        update.channel_post.chat_id = 10
        status.HTTP_201_CREATED = 201
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
        response.assert_called_once_with(status=status.HTTP_201_CREATED)


@pytest.mark.unit
class ProductClassSerializerTest(TestCase):

    def setUp(self):
        self.s = ProductClassSerializer()
        self.s.parsed_data = {}

    def test_initial_name(self):
        self.s.parsed_data['stock'] = {'partner': {'name': "Some partner"}}
        self.assertEqual(self.s.initial_name(), "Some")

    def test_parser(self):
        data = {"name": "name"}
        name, mock_getattr = Mock(), Mock(return_value=lambda : "name")
        name.configure_mock(**{'required': True, "field_name": 'name'})
        self.s.fields = Mock()
        self.s.fields.values.return_value = [name]

        with patch('panda.telegram_bot.serializers.getattr', mock_getattr):
            self.assertEqual(self.s.parser(), data)

        mock_getattr.assert_called_once_with(self.s, 'initial_' + name.field_name, None)

    def test_required_fields(self):
        self.assertListEqual(
            ['name'],
            [field.field_name for field in self.s.fields.values() if field.required]
        )

    def test_order_fields(self):
        self.assertListEqual(
            ['name'],
            self.s.Meta.fields
        )

    def test_create(self):
        validated_data = {"name": "name"}
        self.s.Meta = Mock()
        product_class = Mock()
        self.s.Meta.model.objects.get_or_create.return_value = product_class, False
        self.assertEqual(self.s.create(validated_data), product_class)
        self.s.Meta.model.objects.get_or_create.assert_called_once_with(**validated_data)


@pytest.mark.unit
class StockRecordSerializerTest(TestCase):

    def setUp(self):
        self.s = StockRecordSerializer()
        self.s.parsed_data = {}

    def test_parser(self):
        data = {"partner_sku": 10, "price_excl_tax": 100, "num_in_stock": 10, "partner": "partner"}
        partner_sku, price_excl_tax, num_in_stock, partner = Mock(), Mock(), Mock(), Mock()
        mock_getattr = Mock(
            side_effect=[None, lambda *args: 10, lambda *args: 100, None, lambda *args: 10, None, lambda *args: "partner"]
        )
        partner_sku.configure_mock(**{'required': True, "field_name": 'partner_sku', "read_only": False,
                               "write_only": False, "default": False, "source": ""})
        price_excl_tax.configure_mock(**{'required': True, "field_name": 'price_excl_tax', "read_only": False,
                               "write_only": False, "default": False, "source": ""})
        num_in_stock.configure_mock(**{'required': True, "field_name": 'num_in_stock', "read_only": False,
                               "write_only": False, "default": False, "source": ""})
        partner.configure_mock(**{'required': True, "field_name": 'partner', "read_only": False,
                               "write_only": False, "default": False, "source": ""})
        self.s.fields = Mock()
        self.s.fields.values.return_value = [partner_sku, price_excl_tax, num_in_stock, partner]
        self.s.fields.items.return_value = []
        value = "Some price"

        with patch('panda.telegram_bot.serializers.getattr', mock_getattr):
            self.assertDictEqual(self.s.parser(value), data)

        self.assertListEqual(
            list(mock_getattr.mock_calls),
            [
                call(self.s, 'parse_' + partner_sku.field_name, None),
                call(self.s, 'initial_' + partner_sku.field_name, None),
                call(self.s, 'parse_' + price_excl_tax.field_name, None),
                call(self.s, 'parse_' + num_in_stock.field_name, None),
                call(self.s, 'initial_' + num_in_stock.field_name, None),
                call(self.s, 'parse_' + partner.field_name, None),
                call(self.s, 'initial_' + partner.field_name, None),
            ]
        )

    def test_value_does_not_contain_price(self):
        value = "Wrong price."
        mock_re = Mock(return_value=None)

        with patch('panda.telegram_bot.serializers.re.match', mock_re):
            assert self.s.parse_price_excl_tax(Mock(), value) == ""

        mock_re.assert_called_once_with(r".*[:-]+\s*(?P<price>\d+)(?P<hundredths>\.\d+)*(.*/.*)*", value)

    def test_initial_partner(self):
        field = Mock()
        data = {"name": "name"}
        field.parser.return_value = data
        self.assertDictEqual(self.s.initial_partner(field), data)

    def test_required_fields(self):
        self.assertListEqual(
            ["partner_sku", "price_excl_tax", "num_in_stock", "partner"],
            [field.field_name for field in self.s.fields.values() if field.required]
        )

    def test_order_fields(self):
        self.assertListEqual(
            ["partner_sku", "price_excl_tax", "num_in_stock", "partner"],
            self.s.Meta.fields
        )

    @freeze_time("2019-9-5 14:47:30.538414")
    def test_initial_partner_sku(self):
        upc = 1567694850538414
        mock_datetime_now = Mock(return_value=datetime.datetime.now())

        with patch('panda.telegram_bot.serializers.datetime.datetime.now', mock_datetime_now):
            assert self.s.initial_partner_sku(Mock()) == upc

        mock_datetime_now.assert_called_once_with()

    def test_create(self):
        order = Mock()
        validated_data = {
            "partner_sku": 12,
            "partner": {"name": "name"}
        }
        inp = validated_data.copy()
        stock, product, order.partner, partner = Mock(), Mock(), Mock(), Mock()

        self.s.Meta = Mock()
        self.s.Meta.model.objects.create.return_value = stock
        self.s.fields = {"partner": order.partner}

        order.partner.create.return_value = partner
        order.serializer_meta = self.s.Meta

        exp = {"partner_sku": 12}

        with patch('panda.telegram_bot.serializers.PartnerSerializer', order.partner):
            self.assertEqual(self.s.create(validated_data, product), stock)
            self.assertDictEqual(exp, validated_data)

        self.assertListEqual(
            order.mock_calls,
            [
                call.partner.create(inp['partner']),
                call.serializer_meta.model.objects.create(product=product, partner=partner, **validated_data),
            ]
        )


@pytest.mark.unit
class PartnerSerializerTest(TestCase):

    def setUp(self):
        self.s = PartnerSerializer()
        self.s.parsed_data = {}

    def test_parser(self):
        data = {"name": "name"}
        name, mock_getattr = Mock(), Mock(return_value=lambda : "name")
        name.configure_mock(**{'required': True, "field_name": 'name'})
        self.s.fields = Mock()
        self.s.fields.values.return_value = [name]

        with patch('panda.telegram_bot.serializers.getattr', mock_getattr):
            self.assertEqual(self.s.parser(), data)

        mock_getattr.assert_called_once_with(self.s, 'initial_' + name.field_name, None)

    def test_required_fields(self):
        self.assertListEqual(
            ['name'],
            [field.field_name for field in self.s.fields.values() if field.required]
        )

    def test_order_fields(self):
        self.assertListEqual(
            ['name'],
            self.s.Meta.fields
        )

    def test_create(self):
        validated_data = {"name": "name"}
        self.s.Meta = Mock()
        partner = Mock()
        self.s.Meta.model.objects.get_or_create.return_value = partner, False
        self.assertEqual(self.s.create(validated_data), partner)
        self.s.Meta.model.objects.get_or_create.assert_called_once_with(**validated_data)

@pytest.mark.unit
class ProductImageSerializerTest(TestCase):

    def setUp(self):
        self.s = ProductImageSerializer()

    def test_parser(self):
        pass

    def test_required_fields(self):
        self.assertTupleEqual(
            ('original', ),
            tuple((field.field_name for field in self.s.fields.values() if field.required))
        )

    def test_order_fields(self):
        self.assertTupleEqual(
            ('original', ),
            self.s.Meta.fields
        )

    def test_create(self):
        pass


@pytest.mark.unit
class MessageSerializerTest(TestCase):

    def setUp(self):
        self.s = MessageSerializer()
        self.order = Mock()
        self.create_from_breadcrumbs, self.product, self.product_class_model = Mock(), Mock(), Mock()
        self.create_from_breadcrumbs.return_value = self.create_from_breadcrumbs
        self.s.Meta = Mock()
        self.s.Meta.model.objects.create.return_value = self.product

        self.order.product_class = Mock()
        self.order.message_serializer_meta = self.s.Meta
        self.order.stock_record =Mock()
        self.order.create_from_breadcrumbs = self.create_from_breadcrumbs
        self.order.product_category = Mock()
        self.order.product_class.create.return_value = self.product_class_model
        self.order.image = Mock()

        self.s.fields = {
            "availability": Mock(),
            "stock": self.order.stock_record,
            "image": self.order.image,
            "product_class": self.order.product_class
        }

    # def test_we_make_wrong_price(self):
    #     value = "100didnotsee"
    #     self.assertEqual(self.s.parse_stock(value), {'stock': ''})
    #

    def test_to_internal_value(self):
        inp = {"have_parse": "in_data", "not_have_parse": "in_data"}
        exp = {
            "have_parse": 1,
            "not_have_parse": "in_data",
            "is_required_have_initial": 2,
        }
        have_parse, not_have_parse, is_required_have_initial, not_required_not_have_initial = \
            Mock(), Mock(), Mock(), Mock()
        mock_getattr = Mock(
            side_effect=[lambda *args: 1, None, None, lambda *args: 2, None]
        )
        common = {"read_only": False, "write_only": False, "default": False, "source": ""}
        have_parse.configure_mock(**common, **{'required': True, "field_name": "have_parse"})
        not_have_parse.configure_mock(**common, **{'required': False, "field_name": 'not_have_parse'})
        is_required_have_initial.configure_mock(**common, **{'required': True, "field_name": 'is_required_have_initial'})
        not_required_not_have_initial.configure_mock(**common, **{'required': False, "field_name": 'not_required_not_have_initial'})
        self.s.fields = Mock()
        self.s.fields.values.return_value = [have_parse, not_have_parse, is_required_have_initial, not_required_not_have_initial]
        self.s.fields.items.return_value = []
        super_ = Mock()

        with patch('panda.telegram_bot.serializers.getattr', mock_getattr):
            with patch('panda.telegram_bot.serializers.super', super_):
                self.s.to_internal_value(inp)
                self.assertDictEqual(exp, inp)

        super_ = super_()
        super_.to_internal_value.assert_called_once_with(inp)
        self.assertListEqual(
            list(mock_getattr.mock_calls),
            [
                call(self.s, 'parse_' + have_parse.field_name, None),
                call(self.s, 'parse_' + not_have_parse.field_name, None),
                call(self.s, 'parse_' + is_required_have_initial.field_name, None),
                call(self.s, 'initial_' + is_required_have_initial.field_name, None),
                call(self.s, 'parse_' + not_required_not_have_initial.field_name, None),
            ]
        )

    def test_parse_stock(self):
        self.s.parsed_data = {}
        data = {'partner_sku': "", "price_excl_tax": "", "num_in_stock": "", "partner": ""}
        field = Mock()
        field.parser.return_value = data
        field.field_name = "stock"
        self.assertDictEqual(self.s.parse_stock(field, ""), data)
        self.assertDictEqual(self.s.parsed_data, {"stock": data})

    def test_initial_upc(self):
        self.s.parsed_data['stock'] = {'partner_sku': 121212}
        self.assertEqual(self.s.initial_upc(), 121212)

    def test_initial_product_class(self):
        field = Mock()
        self.s.initial_product_class(field)
        field.parser.assert_called_once_with()

    def test_parse_production_days(self):
        value = 10
        mock_re, mock_int = Mock(), Mock()

        with patch('panda.telegram_bot.serializers.re.match', mock_re):
            with patch('panda.telegram_bot.serializers.int', mock_int):
                self.s.parse_production_days(Mock(), value)

        mock_re.assert_called_once_with(r".*:\s*(?P<days>\d+)(.*)*", value)

    def test_create(self):
        inp = {
            "title": "title",
            "availability": True,
            "category_str": "category_str",
            "production_days": 10,
            "image": {'original': 'file'},
            'stock': {
                "partner_sku": 12, 'partner': {"name": "name"}
            },
            "product_class": {"name": "name"}
        }
        validated_data = inp.copy()
        exp = {"title": "title", "production_days": 10}

        with patch('panda.telegram_bot.serializers.StockRecordSerializer', self.order.stock_record):
            with patch('panda.telegram_bot.serializers.ProductClassSerializer', self.order.product_class):
                with patch('panda.telegram_bot.serializers.create_from_breadcrumbs', self.create_from_breadcrumbs):
                    with patch('panda.telegram_bot.serializers.ProductCategory', self.order.product_category):
                        self.assertEqual(self.s.create(validated_data), self.product)
                        self.assertDictEqual(exp, validated_data)

        self.assertListEqual(
            self.order.mock_calls,
            [
                call.product_class.create(inp['product_class']),
                call.create_from_breadcrumbs(inp['category_str']),
                call.message_serializer_meta.model.objects.create(product_class=self.product_class_model, **validated_data),
                call.product_category.objects.create(product=self.product, category=self.create_from_breadcrumbs),
                call.stock_record.create(inp['stock'], product=self.product),
                call.image.create(inp['image'], product=self.product),
            ]
        )
