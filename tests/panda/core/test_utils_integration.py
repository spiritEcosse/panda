import pytest

from panda.core import utils

data_test_various_slug = (
    ("Компьютер", "kompiuter"),
    ("title change", "title-change"),
)


@pytest.mark.unit
@pytest.mark.parametrize("inp,exp", data_test_various_slug)
def test_slug(inp, exp):
    assert exp == utils.slugify(inp)
