import os
from unittest import TestCase

import pytest
from django.conf import settings
from django.core.files import File
from django.test.utils import override_settings
from django.urls import include, path, reverse
from oscar.core.loading import get_classes
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from panda.telegram_bot.serializers import MessageSerializer, ProductImageSerializer
from panda.telegram_bot.urls import router
from tests.panda.telegram_bot.test_unit import data_test_various_caption

Partner, StockRecord = get_classes('partner.models', ['Partner', 'StockRecord'])
ProductClass, Product, ProductCategory, Category, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'ProductCategory', 'Category', "ProductImage"))

@pytest.mark.integration
class TelegramViewsTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('telegram_bot/', include(router.urls)),
    ]

    def setUp(self):
        self.data = {
            "update_id": 552201929,
            "channel_post": {
                "message_id": 78,
                "media_group_id": "12559467035666010",
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
                        "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA20AA83mAgABFgQ",
                        "width": 320,
                        "height": 90,
                        "file_size": 9260
                    },
                    {
                        "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA3gAA87mAgABFgQ",
                        "width": 800,
                        "height": 225,
                        "file_size": 46171
                    },
                    {
                        "file_id": "AgADAgAD9KwxG1jAOEu4jW4QDw-mEaDWtw8ABAEAAwIAA3kAA8_mAgABFgQ",
                        "width": 1280,
                        "height": 360,
                        "file_size": 104567}
                ],
                "caption": data_test_various_caption[0][0],
                "new_chat_members": [],
                "new_chat_photo": [],
                "delete_chat_photo": False,
                "group_chat_created": False,
                "supergroup_chat_created": False,
                "channel_chat_created": False
            },
        }

    @override_settings(TELEGRAM_HOLD_IMAGE_FILE=True)
    def test_create_product_envs(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse("{}-list".format(settings.HASH))
        response = self.client.post(url, data=self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
        product_image = ProductImage.objects.get(product=product)
        file_path = settings.TELEGRAM_FORMAT_IMAGE_FILE.format(product.upc)
        with File(open(file_path, 'rb')) as image:
            self.assertEqual(product_image.original.read(), image.read())
        os.remove(file_path)

    def test_create_product_envs_only_required_fields(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse("{}-list".format(settings.HASH))
        self.data['channel_post']['caption'] = data_test_various_caption[1][0]
        response = self.client.post(url, data=self.data, format="json")
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
