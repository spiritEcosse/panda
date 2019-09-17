import pytest
from django.test.utils import override_settings
from django.urls import include, path, reverse
from oscar.core.loading import get_classes
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase

from panda.telegram_bot.urls import router
from tests.panda.telegram_bot.test_unit import data_test_various_caption

Partner, StockRecord = get_classes('partner.models', ['Partner', 'StockRecord'])
ProductClass, Product, ProductCategory, Category, ProductImage = get_classes(
    'catalogue.models', ('ProductClass', 'Product', 'ProductCategory', 'Category', "ProductImage"))

@pytest.mark.integration
class AccountTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('telegram_bot/', include(router.urls)),
    ]

    @override_settings(CHAT_ID=10)
    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse("some-list")
        data = {
            "update_id": 552201929,
            "channel_post": {
                "message_id": 78,
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
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        partner = Partner.objects.get(name="Category_str partner")
        product_class = ProductClass.objects.get(name="Category_str")
        product = Product.objects.get(
            title="title", product_class=product_class, description="description\ndescription\ndescription",
            production_days=10, slug="title"
        )
        category = Category.objects.get(name="Sub_category_str")
        self.assertEqual(category.full_name, "Category_str > Sub_category_str")
        ProductCategory.objects.get(product=product, category=category)
        StockRecord.objects.get(
            product=product, partner=partner, price_excl_tax=100, partner_sku=product.upc,
            num_in_stock=0
        )
        # ProductImage.objects.get(product=product, original=File())
