from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError

class MessageException(ValidationError):
    pass
