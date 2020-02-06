import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from telegram import Bot
from telegram.update import Update

from panda.telegram_bot import serializers


class Converter(viewsets.ModelViewSet):
    serializer_class = serializers.MessageSerializer
    lookup_field = "media_group_id"

    def __init__(self, *args, **kwargs):
        self.update_image = False
        super().__init__(*args, **kwargs)

    def get_serializer_class(self):
        if self.update_image:
            return serializers.MessageImageSerializer
        return super().get_serializer_class()

    def get_data(self, update):
        text = update.channel_post.caption.strip()
        values = [value.strip() for value in text.split("\n\n") if value.strip() is not ""]
        data = dict(zip(*(self.serializer_class.Meta.fields, values)))
        media_group_id = self.get_media_group_id(update=update)

        if media_group_id:
            data['media_group_id'] = media_group_id

        data.update(self.get_data_image(update=update))
        return data

    def get_data_image(self, **kwargs):
        data = dict()
        data['image'] = {}
        data['image']['original'] = kwargs['update'].channel_post.photo[-1].get_file()
        return data

    def get_media_group_id(self, **kwargs):
        return getattr(kwargs['update'].channel_post, 'media_group_id', None)

    def get_object(self, **kwargs):
        update = kwargs['update']

        try:
            media_group_id = self.get_media_group_id(update=update)
            if media_group_id:
                return self.serializer_class.Meta.model.objects.get(
                    **{self.lookup_field: media_group_id}
                )
        except ObjectDoesNotExist:
            pass

    def update(self, request, *args, **kwargs): # ToDo add edited_channel_post
        instance = self.get_object(**kwargs)
        self.update_image = True
        serializer = self.get_serializer(
            instance, data=self.get_data_image(**kwargs), partial=True
        )

        if not serializer.is_valid(raise_exception=False):
            raise ValidationError(serializer.errors, serializer.data)
        serializer.save()

    def create(self, request, *args, **kwargs):
        bot = Bot(settings.TOKEN_TELEGRAM)
        update = Update.de_json(json.loads(request.body), bot)

        if update.channel_post.chat_id == settings.CHAT_ID:
            if self.get_object(update=update):
                self.update(request, *args, update=update, **kwargs)
                return Response(status=status.HTTP_200_OK)

            serializer = self.get_serializer(data=self.get_data(update))
            if not serializer.is_valid(raise_exception=False):
                raise Exception(serializer.errors, serializer.data)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
