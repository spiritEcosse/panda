import pytest
from django.test import TestCase
from django.test.utils import override_settings
from oscar.core.loading import get_classes

Product, ProductClass = get_classes('catalogue.models', ('Product', 'ProductClass'))


class ProductTests(TestCase):

    def setUp(self):
        self.product_class, _ = ProductClass.objects.get_or_create(
            name='Clothing')


@pytest.mark.integration
class ProductTest(ProductTests):
    @override_settings(OSCAR_SLUG_FUNCTION="panda.core.utils.slugify")
    def test_slug(self):
        exp = "kompiuter"
        product = Product(title="Компьютер", product_class=self.product_class)
        product.save()
        self.assertEqual(product.slug, exp)
