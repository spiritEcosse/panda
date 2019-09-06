from rest_framework import routers

from panda.telegram_bot.views import Converter

router = routers.SimpleRouter()
router.register(r'some', Converter, basename="some")
