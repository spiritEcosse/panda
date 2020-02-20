import json

from django.conf import settings
from django.http import Http404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from telegram import Bot
from telegram.update import Update

from panda.telegram_bot import serializers


class Converter(viewsets.ModelViewSet):
    serializer_class = serializers.MessageSerializer
    queryset = serializer_class.Meta.model.objects.all()
    lookup_field = "message_id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_post = None

    def get_data(self):
        text = self.channel_post.caption.strip()
        values = [value.strip() for value in text.split("\n\n") if value.strip() is not ""]
        data = dict(zip(*(self.serializer_class.Meta.caption_fields, values)))
        data.update({'message_id': self.channel_post.message_id})
        media_group_id = self.get_media_group_id()

        if media_group_id:
            data['media_group_id'] = media_group_id

        data.update(self.get_data_image())
        return data

    def get_data_image(self):
        data = dict()
        data['image'] = {}
        data['image']['original'] = self.channel_post.photo[-1].get_file()
        return data

    def get_media_group_id(self):
        return getattr(self.channel_post, 'media_group_id', None)

    def get_object(self, **kwargs):
        update = kwargs['update']

        try:
            lookup_field = update.edited_channel_post.message_id
        except AttributeError:
            lookup_field = self.get_media_group_id()

            if lookup_field:
                self.lookup_field = 'media_group_id'

        self.kwargs[self.lookup_field] = lookup_field
        return super().get_object()

    def update(self, request, *args, **kwargs):
        instance = self.get_object(**kwargs)
        serializer = self.get_serializer(instance, data=self.get_data(), partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def create(self, request, *args, **kwargs):
        bot = Bot(settings.TOKEN_TELEGRAM)
        update = Update.de_json(json.loads(request.body), bot)

        self.channel_post = update.channel_post or update.edited_channel_post
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if self.channel_post.chat_id == settings.CHAT_ID:
            try:
                self.get_object(update=update)
                self.update(request, *args, update=update, **kwargs)
                status_code = status.HTTP_200_OK
            except Http404:
                serializer = self.get_serializer(data=self.get_data())
                serializer.is_valid(raise_exception=True)
                serializer.save()
                status_code = status.HTTP_201_CREATED

        return Response(status=status_code)
