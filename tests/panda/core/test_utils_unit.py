from unittest import TestCase
from unittest.mock import patch, Mock

from panda.core import utils


class TestSlugify(TestCase):

    def test_slugify(self):
        slugify = Mock()
        text = "Some"
        slugify.return_value = "some"

        with patch('panda.core.utils.slugify', slugify):
            self.assertEqual('some', utils.slugify(text))

        slugify.assert_called_once_with(text)
