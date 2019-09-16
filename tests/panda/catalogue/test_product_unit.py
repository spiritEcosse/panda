from unittest import TestCase
from unittest.mock import patch, Mock, call

import pytest
from oscar.core.loading import get_class

Product = get_class('catalogue.models', 'Product')

@pytest.mark.unit
class ProductTest(TestCase):
    def test_save(self):
        exp = "title"
        title = "Title"
        order = Mock()
        order.slugify.return_value = exp
        self.product = Product(title=title)
        self.product.attr = Mock()
        self.product.get_title = Mock()
        self.product.get_title.return_value = title
        args = []
        kwargs = {}
        with patch('oscar.apps.catalogue.abstract_models.slugify', order.slugify):
            with patch('oscar.apps.catalogue.abstract_models.super', order.super_):
                self.product.save(*args, **kwargs)
                self.assertEqual(self.product.slug, exp)

        self.assertListEqual(
            order.mock_calls,
            [
                call.slugify(self.product.get_title()),
                call.super_(),
                call.super_().save(*args, **kwargs),
            ]
        )
