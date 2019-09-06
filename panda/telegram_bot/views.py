import csv
import json
import uuid

from django.conf import settings
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from telegram import Bot
from telegram.update import Update

from panda.telegram_bot.serializers import MessageSerializer


class Converter(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    file_mask = "{}.csv"

    def __init__(self, *args, **kwargs):
        self.request = None
        self.file_name = self.file_mask.format(uuid.uuid4())
        super().__init__(*args, **kwargs)

    def write(self, serializer):
        with open(self.file_name, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(serializer.validated_data.values())

    def get_data(self, update):
        text = update.channel_post.caption.strip()
        values = filter(lambda el: el is not "", text.split("\n"))
        return dict(zip(*(self.serializer_class.Meta.fields, values)))

    def create(self, request, *args, **kwargs):
        self.request = request

        bot = Bot(settings.TOKEN_TELEGRAM)
        update = Update.de_json(json.loads(self.request.body), bot)

        # ToDo replace on wrapper
        if update.channel_post.chat_id == settings.CHAT_ID:
            serializer = self.get_serializer(data=self.get_data(update))
            serializer.is_valid(raise_exception=True)
            self.write(serializer)
            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
