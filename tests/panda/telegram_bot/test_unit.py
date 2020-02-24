import datetime
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock, call

import pytest
from django.conf import settings
from django.http import Http404
from django.test.utils import override_settings
from freezegun import freeze_time
from rest_framework.serializers import ValidationError
from rest_framework import status

from panda.telegram_bot.serializers import MessageSerializer, StockRecordSerializer, \
    ProductClassSerializer, PartnerSerializer, ProductImageSerializer
from panda.telegram_bot.views import Converter

data_test_various_caption = (
    ("title\n\navailability\n\nPrice: 100$\n\ndescription\ndescription\ndescription\n\n"
     "category_str>sub_category_str\n\nproduction days: 10 days.",
     {"title": "title", "availability": "availability", "stock": "Price: 100$",
      "description": "description\ndescription\ndescription", "category_str": "category_str>sub_category_str",
      "production_days": "production days: 10 days.", "image": {'original': 'some'},
      "media_group_id": "12345", 'message_id': 1
      }),
    ("title\n\navailability\n\nPrice: 100$\n\ndescription\ndescription\ndescription\n\n"
     "category_str>sub_category_str",
     {"title": "title", "availability": "availability", "stock": "Price: 100$",
      "description": "description\ndescription\ndescription", "category_str": "category_str>sub_category_str",
      "image": {'original': 'some'},
      "media_group_id": "12345", 'message_id': 1
      }),
    ("\n\n\r\ttitle change\n\n\r\navailability\n\n\rPrice: 100$\n\n\t\rdescription\n\n\r"
     "category_str>category_str",
     {"title": "title change", "availability": "availability", "stock": "Price: 100$",
      "description": "description", "category_str": "category_str>category_str", "image": {'original': 'some'},
      'message_id': 1
      }),
)


data_test_various_price = (
    ("Цена: 100$", "100"),
    ("Price: 100$", "100"),
    ("Price: 100$/50€", "100"),
    ("Price:100$/50€", "100"),
    ("Price:100$ / 50€", "100"),
    ("Price:  100$  / 50€", "100"),
    ("Price:  100.90", "100.90"),
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
    channel_post = Mock()
    channel_post.caption = inp
    file_ = Mock()
    file_.get_file.return_value= "some"
    channel_post.photo = [file_]
    channel_post.media_group_id = exp.get('media_group_id', None)
    channel_post.message_id = exp['message_id']
    converter = Converter()
    converter.channel_post = channel_post
    assert converter.get_data() == exp

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


class CommonSerializerTest(TestCase):
    __test__ = False

    def setUp(self):
        self.s = None

    def test_parser(self):
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

        with patch('panda.telegram_bot.serializers.getattr', mock_getattr):
            self.s.parser(inp)
            self.assertDictEqual(exp, inp)

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


@pytest.mark.unit
class MessagesTest(TestCase):

    def setUp(self):
        self.converter = Converter()
        self.converter.kwargs = {}
        self.order = Mock()
        self.obj = Mock()
        self.order.super = Mock(**{"get_object.return_value": self.obj})
        self.converter.get_media_group_id = self.order.get_media_group_id = Mock(return_value=None)
        self.converter.get_data = self.order.get_data = Mock()
        self.converter.bot_update = Mock(edited_channel_post=None)
        self.calls = [
            call.super.get_object(),
        ]

    # create
    def mock_create(self):
        order, request, bot_obj, get_data = Mock(), Mock(data={}), Mock(), Mock()
        order.bot, order.serializer = Mock(return_value=bot_obj), Mock()
        update_bot_obj, order.status =\
            Mock(**{'channel_post.chat_id': 10}), Mock(
                HTTP_201_CREATED=status.HTTP_201_CREATED, HTTP_200_OK=status.HTTP_200_OK
            )
        self.converter.get_data = order.get_data = Mock(return_value=get_data)
        self.converter.get_serializer = order.get_serializer = Mock(return_value=order.serializer)
        self.converter.get_object = order.get_object = Mock()
        self.converter.update = order.update = Mock()

        order.update_bot = Mock(return_value=update_bot_obj)
        args = (request, )
        kwargs = {}
        calls = [
            call.bot(settings.TOKEN_TELEGRAM),
            call.update_bot(request.data, bot_obj),
        ]
        return calls, order, kwargs, args, get_data, update_bot_obj

    @override_settings(CHAT_ID=11)
    @override_settings(TOKEN_TELEGRAM="some")
    def test_wrong_chat_id(self):
        request, update, response, status_code, settings, bot = \
            Mock(data={}), Mock(), Mock(), Mock(HTTP_500_INTERNAL_SERVER_ERROR=status.HTTP_500_INTERNAL_SERVER_ERROR), Mock(), Mock()
        update.channel_post.chat_id = 10
        request.body = "json"
        update = Mock(return_value=update)

        with patch('panda.telegram_bot.views.Bot', bot):
            with patch('panda.telegram_bot.views.Update.de_json', update):
                with patch('panda.telegram_bot.views.Response', response):
                    self.converter.create(request)

        bot.assert_called_once_with("some")
        update.assert_called_once_with(request.data, bot())
        response.assert_called_once_with(status=status_code.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_create(self):
        calls, order, kwargs, args, get_data, update_bot_obj = self.mock_create()
        order.get_object.side_effect = Http404
        self.run_create(calls, order, kwargs, args, get_data)
        self.assertListEqual(order.mock_calls, calls + [
            call.get_object(),
            call.get_data(),
            call.get_serializer(data=get_data),
            call.serializer.is_valid(raise_exception=True),
            call.serializer.save(),
            call.response(status=order.status.HTTP_201_CREATED)
        ])

    def test_create_update(self):
        calls, order, kwargs, args, _, update_bot_obj = self.mock_create()
        self.run_create(calls, order, kwargs, args, _)
        self.assertListEqual(order.mock_calls, calls + [
            call.get_object(),
            call.update(*args, **kwargs),
            call.response(status=order.status.HTTP_200_OK)
        ])

    def test_create_delete(self):
        calls, order, kwargs, args, _, update_bot_obj = self.mock_create()
        update_bot_obj.channel_post = None
        update_bot_obj.edited_channel_post = Mock(caption=None, chat_id=10)
        destroy_obj = Mock()
        self.converter.destroy = order.destroy = Mock(return_value=destroy_obj)

        obj = self.run_create(calls, order, kwargs, args, _)
        self.assertListEqual(order.mock_calls, calls + [
            call.destroy(*args, **kwargs)
        ])
        self.assertEqual(obj, destroy_obj)

    def run_create(self, calls, order, kwargs, args, get_data):
        with patch('panda.telegram_bot.views.Bot', order.bot):
            with patch('panda.telegram_bot.views.Update.de_json', order.update_bot):
                with patch('panda.telegram_bot.views.Response', order.response):
                    return self.converter.create(*args)

    # update
    def mock_update(self):
        """Initial mocks for update method"""

        order, request, instance, get_data, update = Mock(), Mock(), Mock(), Mock(), Mock()
        order.serializer = Mock(**{'save.return_value': Mock(), 'is_valid.return_value': False})
        self.converter.get_object = order.get_object = Mock(return_value=instance)
        self.converter.get_serializer = order.get_serializer = Mock(return_value=order.serializer)
        self.converter.get_data = order.get_data = Mock(return_value=get_data)
        kwargs = {}
        args = (request, )
        calls = [
            call.get_object(**kwargs),
            call.get_data(**kwargs),
            call.get_serializer(instance, data=get_data, partial=True),
            call.serializer.is_valid(raise_exception=True),
        ]
        return calls, order, kwargs, args

    def test_update_validation_error(self):
        """Test update when raised ValidationError"""

        calls, order, kwargs, args = self.mock_update()
        order.serializer.is_valid.side_effect = ValidationError

        with self.assertRaises(ValidationError):
            self.converter.update(*args, kwargs)
        self.assertListEqual(order.mock_calls, calls)

    def test_update(self):
        """Test update when saved data to db"""

        calls, order, kwargs, args = self.mock_update()

        self.converter.update(*args, kwargs)
        self.assertListEqual(order.mock_calls, calls + [call.serializer.save()])

    # get_object
    def test_get_object_not_update(self):
        """Test get_object when nothing pass"""

        with patch('panda.telegram_bot.views.super', Mock(return_value=self.order.super)):
            self.assertEqual(self.obj, self.converter.get_object())
            self.assertListEqual(self.order.mock_calls, [call.get_media_group_id()] + self.calls)
            self.assertDictEqual({'message_id': None}, self.converter.kwargs)

    def test_get_object_exist_media_group_id(self):
        """Test get_object when exist media_group_id"""

        media_group_id = 1
        self.converter.get_media_group_id = self.order.get_media_group_id = Mock(return_value=media_group_id)

        with patch('panda.telegram_bot.views.super', Mock(return_value=self.order.super)):
            self.assertEqual(self.obj, self.converter.get_object())
            self.assertListEqual(self.order.mock_calls, [call.get_media_group_id()] + self.calls)
            self.assertDictEqual({'media_group_id': media_group_id}, self.converter.kwargs)

    def test_get_object_exist_message_id(self):
        """Test get_object when exist message_id"""

        message_id = 12
        self.converter.channel_post = Mock(message_id=message_id)

        with patch('panda.telegram_bot.views.super', Mock(return_value=self.order.super)):
            self.assertEqual(self.obj, self.converter.get_object())
            self.assertListEqual(self.order.mock_calls, self.calls)
            self.assertDictEqual({'message_id': message_id}, self.converter.kwargs)

    # get_data_image
    def test_get_data_image(self):
        file_ = Mock()
        photo = Mock(**{'get_file.return_value': file_})
        channel_post = Mock(**{'photo': [photo]})
        self.converter.channel_post = channel_post
        self.assertDictEqual({'image': {'original': file_}}, self.converter.get_data_image())
        photo.get_file.assert_called_once_with()


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

        mock_re.assert_called_once_with(r".*:\s*(?P<price>\d+)(?P<hundredths>\.\d+)*(.*/.*)*", value)

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
        self.order, self.product = Mock(), Mock()
        self.order.product_image_model, self.order.os = Mock(), Mock()
        self.order.meta = self.s.Meta = Mock()
        self.order.meta.model.return_value = self.order.product_image_model

    @override_settings(TELEGRAM_HOLD_IMAGE_FILE=False)
    def test_create(self):
        self.file = Mock()
        file_name = ["name_file.jpg"]
        self.file.name.split.return_value = file_name
        inp = {
            "original": self.file,
        }
        exp = {}
        validated_data = inp.copy()

        with patch('panda.telegram_bot.serializers.ProductImage', self.order.product_image):
            with patch('panda.telegram_bot.serializers.os', self.order.os):
                self.s.create(validated_data, self.product)
                self.assertDictEqual(exp, validated_data)

        self.assertListEqual(
            self.order.mock_calls,
            [
                call.meta.model(product=self.product, **validated_data),
                call.product_image_model.original.save(file_name[-1], inp['original'], save=False),
                call.product_image_model.save(),
                call.os.remove(inp['original'].name)
            ]
        )

    @override_settings(TELEGRAM_FORMAT_IMAGE_FILE="media/images/{}.jpg")
    def test_parse_original(self):
        file_name = "12345"
        file_path = "media/images/{}.jpg".format(file_name)
        self.order, self.open_file = Mock(), Mock()
        self.order.value = value = Mock(file_id=file_name)
        self.order.image, self.order.file, self.order.mo, self.open_image = \
            Mock(**{'open.return_value': self.order.open_image}), Mock(), Mock(), Mock()
        self.order.mo.return_value = self.open_file
        value.download.return_value = True

        with patch('panda.telegram_bot.serializers.Image', self.order.image):
            with patch('panda.telegram_bot.serializers.open', self.order.mo):
                with patch('panda.telegram_bot.serializers.File', self.order.file):
                    self.s.parse_original(Mock(), value)

        self.assertListEqual(
            self.order.mock_calls,
            [
                call.value.download(file_path),
                call.image.open(file_path),
                call.open_image.verify(),
                call.mo(file_path, 'rb'),
                call.file(self.open_file)
            ]
        )


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

    def test_to_internal_value(self): # ToDo make easy, exactly
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
        super_.to_internal_value.assert_called_once_with(exp)
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

    def test_parse_image(self):
        field = Mock()
        value = "file"
        self.s.parse_image(field, value)
        field.parser.assert_called_once_with(value)

    def test_initial_production_days(self):
        self.assertIsNone(self.s.initial_production_days())

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

    def test_update(self):
        inp = {
            "title": "title",
            "availability": True,
            "category_str": "category_str",
            "production_days": None,
            "image": {'original': 'file'},
            'stock': {
                "partner_sku": 12, 'partner': {"name": "name"}
            },
            "product_class": {"name": "name"}
        }
        validated_data = inp.copy()
        exp = {"title": "title", "production_days": None}

        with patch('panda.telegram_bot.serializers.StockRecordSerializer', self.order.stock_record):
            with patch('panda.telegram_bot.serializers.create_from_breadcrumbs', self.create_from_breadcrumbs):
                with patch('panda.telegram_bot.serializers.ProductCategory', self.order.product_category):
                    self.assertEqual(self.s.update(self.product, validated_data), self.product)
                    self.assertDictEqual(exp, validated_data)

        self.assertListEqual(
            self.order.mock_calls,
            [
                call.create_from_breadcrumbs(inp['category_str']),
                call.product_category.objects.get_or_create(product=self.product, category=self.create_from_breadcrumbs),
                call.stock_record.create(inp['stock'], product=self.product),
                call.message_serializer_meta.model.objects.update(id=self.product.id, **validated_data),
                call.image.create(inp['image'], product=self.product),
            ]
        )

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
                call.message_serializer_meta.model.objects.create(
                    product_class=self.product_class_model, **validated_data
                ),
                call.product_category.objects.create(product=self.product, category=self.create_from_breadcrumbs),
                call.stock_record.create(inp['stock'], product=self.product),
                call.image.create(inp['image'], product=self.product),
            ]
        )
