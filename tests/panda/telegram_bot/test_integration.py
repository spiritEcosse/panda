import os
import shutil
from decimal import *
from unittest import TestCase
from unittest.mock import patch, Mock

import pytest
from PIL import Image
from django.conf import settings
from django.test.utils import override_settings
from django.urls import include, path, reverse
from django.utils import timezone
from oscar.core.loading import get_classes
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from panda.catalogue.apps import CatalogueConfig
from panda.telegram_bot.serializers import MessageSerializer, ProductImageSerializer
from panda.telegram_bot.urls import router

Partner, StockRecord = get_classes('partner.models', ['Partner', 'StockRecord'])
ProductClass, Product, ProductCategory, Category, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'ProductCategory', 'Category', "ProductImage"))

media_group_id = "12559467035666010"
message_id = 78

data_test_various_caption = (
    ("title\n\navailability\n\nPrice: 100$\n\ndescription\ndescription\ndescription\n\n"
     "category_str>sub_category_str\n\nproduction days: 10 days.",
     {"title": "title", "availability": "availability", "stock": Decimal('100.00'),
      "description": "description\ndescription\ndescription", "category": "Sub_category_str",
      "category_full": "Category_str > Sub_category_str",
      "production_days": 10
      }),
    ("title\n\navailability\n\nPrice: 100$\n\ndescription\ndescription\ndescription\n\n"
     "category_str>sub_category_str",
     {"title": "title", "availability": "availability", "stock": Decimal('100.00'),
      "production_days": None, "description": "description\ndescription\ndescription", "category": "Sub_category_str",
      "category_full": "Category_str > Sub_category_str"
      }),
    ("\n\n\r\ttitle change\n\n\r\navailability\n\n\rPrice: 200$\n\n\t\rdescription\n\n\r"
     "category_str>other_category_str",
     {"title": "title change", "availability": "availability", "stock": Decimal('200.00'),
      "production_days": None, "description": "description", "category": "Other_category_str",
      "category_full": "Category_str > Other_category_str"
      }),
)

data_test_create_product = (
    ({
        "update_id": 552201929,
        "channel_post": {
            "message_id": message_id,
            "media_group_id": media_group_id,
            "date": 1567772991,
            "chat": {
                "id": 10,
                "type": "channel",
                "title": "test_channel",
                "username": "test_channellllllllll"
            },
            "entities": [],
            "caption_entities": [],
            "photo": [
                {
                    "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgA",
                    "width": 320,
                    "height": 90,
                    "file_size": 9260
                },
                {
                    "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgB",
                    "width": 800,
                    "height": 225,
                    "file_size": 46171
                },
                {
                    "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgC",
                    "width": 1280,
                    "height": 360,
                    "file_size": 104567
                }
            ],
            "caption": data_test_various_caption[0][0],
            "new_chat_members": [],
            "new_chat_photo": [],
            "delete_chat_photo": False,
            "group_chat_created": False,
            "supergroup_chat_created": False,
            "channel_chat_created": False
        }
    }, status.HTTP_201_CREATED,),
    ({
        "update_id": 552201929,
        "channel_post": {
            "message_id": message_id,
            "media_group_id": media_group_id,
            "date": 1567772991,
            "chat": {
                "id": 10,
                "type": "channel",
                "title": "test_channel",
                "username": "test_channellllllllll"
            },
            "entities": [],
            "caption_entities": [],
            "photo": [
                {
                    "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgD",
                    "width": 320,
                    "height": 90,
                    "file_size": 9260
                },
                {
                    "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgE",
                    "width": 800,
                    "height": 225,
                    "file_size": 46171
                },
                {
                    "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgF",
                    "width": 1280,
                    "height": 360,
                    "file_size": 104567
                }
            ],
            "caption": data_test_various_caption[1][0],
            "new_chat_members": [],
            "new_chat_photo": [],
            "delete_chat_photo": False,
            "group_chat_created": False,
            "supergroup_chat_created": False,
            "channel_chat_created": False
        }
    }, status.HTTP_200_OK),
    ({
        "update_id": 552201929,
        "edited_channel_post": {
            "message_id": message_id,
            "media_group_id": media_group_id,
            "date": 1567772991,
            "chat": {
                "id": 10,
                "type": "channel",
                "title": "test_channel",
                "username": "test_channellllllllll"
            },
            "entities": [],
            "caption_entities": [],
            "photo": [
                {
                    "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgD",
                    "width": 320,
                    "height": 90,
                    "file_size": 9260
                },
                {
                    "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgE",
                    "width": 800,
                    "height": 225,
                    "file_size": 46171
                },
                {
                    "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgF",
                    "width": 1280,
                    "height": 360,
                    "file_size": 104567}
            ],
            "caption": data_test_various_caption[2][0],
            "new_chat_members": [],
            "new_chat_photo": [],
            "delete_chat_photo": False,
            "group_chat_created": False,
            "supergroup_chat_created": False,
            "channel_chat_created": False
        }
    }, status.HTTP_200_OK),
)


def create_product(self, index):
    caption_exp = data_test_various_caption[index][1]
    inp, exp = data_test_create_product[index]
    url = reverse("{}-list".format(settings.HASH))

    if 'channel_post' in inp:
        channel_post = inp['channel_post']
    else:
        channel_post = inp['edited_channel_post']

    file_name = channel_post['photo'][-1]['file_id']
    file_path = settings.TELEGRAM_FORMAT_IMAGE_FILE.format(file_name)
    download = Mock(side_effect=self.create_img)
    file_ = Mock(file_id=file_name, **{'download': download})

    with patch('panda.telegram_bot.views.Bot.get_file', Mock(return_value=file_)):
        response = self.client.post(url, data=inp, format="json")

    path_ = os.path.join(self.image_folder, '{}.jpg'.format(file_name))

    self.assertEqual(response.status_code, exp)

    category_main = caption_exp['category_full'].split(">")[0].strip()
    partner = Partner.objects.get(name="{} partner".format(category_main))
    product = Product.objects.get(message_id=message_id)
    product_class = ProductClass.objects.get(name=category_main)

    self.assertEqual(product.title, caption_exp["title"])
    self.assertEqual(product.product_class, product_class)
    self.assertEqual(product.description, caption_exp["description"])
    self.assertEqual(product.production_days, caption_exp['production_days'])
    self.assertEqual(product.media_group_id, media_group_id)

    product_image = ProductImage.objects.get(product=product, original=path_)
    self.assertEqual(product_image.original.name, path_)
    os.remove(file_path)

    category = Category.objects.get(name=caption_exp['category'])
    self.assertEqual(category.full_name, caption_exp['category_full'])

    ProductCategory.objects.get(product=product, category=category)

    stock = StockRecord.objects.filter(product=product).last()
    self.assertEqual(stock.price_excl_tax, caption_exp['stock'])
    self.assertEqual(stock.partner, partner)
    self.assertEqual(stock.num_in_stock, 0)
    self.assertEqual(stock.partner_sku, product.upc)


@pytest.mark.integration
class TelegramViewsTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('telegram_bot/', include(router.urls)),
    ]

    def setUp(self):
        self.image_folder = timezone.now().strftime(settings.OSCAR_IMAGE_FOLDER)

    def tearDown(self):
        root_image_folder = os.sep.join(self.image_folder.split(os.sep)[:2])
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, root_image_folder), ignore_errors=True)

    @staticmethod
    def create_img(value):
        img = Image.new('RGB', (1, 1))
        img.save(value)
        return True

    @override_settings(TELEGRAM_HOLD_IMAGE_FILE=True)
    def test_create_product_envs(self):
        """
        Ensure we can create a new account object.
        """
        create_product(self, 0)
        create_product(self, 1)
        create_product(self, 2)
        self.assertEqual(1, Product.objects.count())

    def test_create_product_envs_only_required_fields(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse("{}-list".format(settings.HASH))
        data = data_test_create_product[1][0]

        file_name = data['channel_post']['photo'][-1]['file_id']
        download = Mock(side_effect=self.create_img)
        file_ = Mock(file_id=file_name, **{'download': download})

        with patch('panda.telegram_bot.views.Bot.get_file', Mock(return_value=file_)):
            response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        product_class = ProductClass.objects.get(name="Category_str")
        Product.objects.get(
            title="title", product_class=product_class, description="description\ndescription\ndescription",
            production_days=None, slug="title"
        )


@pytest.mark.integration
class MessageSerializerTest(TestCase):
    def setUp(self):
        self.s = MessageSerializer()

    def test_required_fields(self):
        self.assertTupleEqual(
            ('title', "availability", 'stock', 'description', "category_str", "production_days",
             "product_class", "upc", "image", "message_id"),
            tuple(field.field_name for field in self.s.fields.values() if field.required)
        )

    def test_order_fields(self):
        self.assertTupleEqual(
            ('title', "availability", 'stock', 'description', "category_str",
             "production_days", "product_class", "upc", "image", "media_group_id", "message_id"),
            self.s.Meta.fields
        )


@pytest.mark.integration
class ProductImageSerializerTest(TestCase):
    def setUp(self):
        self.s = ProductImageSerializer()

    def test_order_fields(self):
        self.assertTupleEqual(
            ('original', ),
            self.s.Meta.fields
        )

    def test_required_fields(self):
        self.assertTupleEqual(
            ('original', ),
            tuple((field.field_name for field in self.s.fields.values() if field.required))
        )


class CatalogueConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(CatalogueConfig.name, 'panda.catalogue')
