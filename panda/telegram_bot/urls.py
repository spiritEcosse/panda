from django.conf import settings
from rest_framework import routers

from panda.telegram_bot.views import Converter

router = routers.SimpleRouter()
router.register(settings.HASH, Converter, basename=settings.HASH)
