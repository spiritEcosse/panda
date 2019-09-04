from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError

class MessageException(ValidationError):
    default_detail = _("Wrong field price.")

    def __init__(self, *args, **kwargs):
        super().__init__(self.default_detail, *args, **kwargs)
