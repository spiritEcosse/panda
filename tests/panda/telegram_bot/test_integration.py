import os
import shutil
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

from panda.telegram_bot.serializers import MessageSerializer, ProductImageSerializer
from panda.telegram_bot.urls import router
from tests.panda.telegram_bot.test_unit import data_test_various_caption

Partner, StockRecord = get_classes('partner.models', ['Partner', 'StockRecord'])
ProductClass, Product, ProductCategory, Category, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'ProductCategory', 'Category', "ProductImage"))

media_group_id = "12559467035666010"

# {
#   "update_id": 386414751,
#   "edited_channel_post": {
#     "message_id": 154,
#     "chat": {
#       "id": -1001241134985,
#       "title": "test_channel",
#       "username": "test_channellllllllll",
#       "type": "channel"
#     },
#     "date": 1580804243,
#     "edit_date": 1580805706,
#     "text": "dfdddddddddddddddd"
#   }
# }

data_test_create_product = (
    ({
        "update_id": 552201929,
        "channel_post": {
            "message_id": 78,
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
            "message_id": 78,
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
            "caption": data_test_various_caption[1][0],
            "new_chat_members": [],
            "new_chat_photo": [],
            "delete_chat_photo": False,
            "group_chat_created": False,
            "supergroup_chat_created": False,
            "channel_chat_created": False
        }
    }, status.HTTP_200_OK),
)

def create_product(self, inp, exp):
    url = reverse("{}-list".format(settings.HASH))
    file_name = inp['channel_post']['photo'][-1]['file_id']
    file_path = settings.TELEGRAM_FORMAT_IMAGE_FILE.format(file_name)

    download = Mock(side_effect=self.create_img)
    file_ = Mock(file_id=file_name, **{'download': download})

    with patch('panda.telegram_bot.views.Bot.get_file', Mock(return_value=file_)):
        response = self.client.post(url, data=inp, format="json")
    print(response.content)
    self.assertEqual(response.status_code, exp)

    partner = Partner.objects.get(name="Category_str partner")
    product_class = ProductClass.objects.get(name="Category_str")
    product = Product.objects.get(
        title="title", product_class=product_class, description="description\ndescription\ndescription",
        production_days=10, slug="title", media_group_id="12559467035666010"
    )
    category = Category.objects.get(name="Sub_category_str")
    self.assertEqual(category.full_name, "Category_str > Sub_category_str")
    ProductCategory.objects.get(product=product, category=category)
    StockRecord.objects.get(
        product=product, partner=partner, price_excl_tax=100, partner_sku=product.upc,
        num_in_stock=0
    )
    path_ = os.path.join(self.image_folder, '{}.jpg'.format(file_name))
    product_image = ProductImage.objects.get(product=product, original=path_)
    self.assertEqual(product_image.original.name, path_)
    os.remove(file_path)

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
        create_product(self, *data_test_create_product[0])
        create_product(self, *data_test_create_product[1])

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
        self.assertListEqual(
            ['title', "availability", 'stock', 'description', "category_str", "product_class", "upc", "image"],
            [field.field_name for field in self.s.fields.values() if field.required]
        )

    def test_order_fields(self):
        self.assertListEqual(
            ['title', "availability", 'stock', 'description', "category_str",
             "production_days", "product_class", "upc", "image", "media_group_id"],
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
