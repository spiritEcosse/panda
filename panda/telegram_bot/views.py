import csv
import uuid

from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action

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

    def get_data(self):
        text = self.request.data.channel_post.caption.strip()
        values = filter(lambda el: el is not "", text.split("\n"))
        return dict(zip(*(self.serializer_class.Meta.fields, values)))

    @action(detail=False, methods=['post'])
    def run(self, request):
        self.request = request

        # ToDo replace on wrapper
        if self.request.data.channel_post.chat_id == settings.CHAT_ID:
            serializer = self.get_serializer(data=self.get_data())
            serializer.is_valid(raise_exception=True)
            self.write(serializer)
            return True

# def run():
#     messageHandler = MessageHandler(Filters.all, receive_message)
#     updater = Updater(
#         token = settings.TOKEN_TELEGRAM,
#         request_kwargs={'read_timeout': 10, 'connect_timeout': 10}
#     )
#     updater.dispatcher.add_handler(messageHandler)
#     updater.start_webhook(
#         listen = '0.0.0.0',
#         port = 443,
#         url_path = settings.TOKEN_TELEGRAM
#     )
#     updater.bot.set_webhook(
#         webhook_url='https://{}:{}/{}'.format("176.36.12.87", 443, settings.TOKEN_TELEGRAM),
#         certificate = open('cert.pem', 'rb')
#     )
#     # updater.start_webhook(
#     #     listen='0.0.0.0',
#     #     port=443,
#     #     url_path=settings.TOKEN_TELEGRAM,
#     #     key='private.key',
#     #     cert='cert.pem',
#     #     webhook_url='https://{}:{}/{}'.format("176.36.12.87", 443, settings.TOKEN_TELEGRAM)
#     # )
#
# if __name__ == "__main__":
#     run()
#
