from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


class MessageException(ValidationError):
    default_detail = _("Wrong field price.")
