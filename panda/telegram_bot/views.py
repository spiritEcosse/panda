import json

from django.conf import settings
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from telegram import Bot
from telegram.update import Update

from panda.telegram_bot.serializers import MessageSerializer


class Converter(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def get_data(self, update):
        text = update.channel_post.caption.strip()
        values = [value.strip() for value in text.split("\n\n") if value.strip() is not ""]
        data = dict(zip(*(self.serializer_class.Meta.fields, values)))
        data['image'] = update.channel_post.photo[-1].get_file()
        return data

    def create(self, request, *args, **kwargs):
        bot = Bot(settings.TOKEN_TELEGRAM)
        update = Update.de_json(json.loads(request.body), bot)

        if update.channel_post.chat_id == settings.CHAT_ID:
            serializer = self.get_serializer(data=self.get_data(update))
            if not serializer.is_valid(raise_exception=False):
                raise Exception(serializer.errors, serializer.data)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
