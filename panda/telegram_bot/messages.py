import csv
import uuid

from django.conf import settings
from telegram.ext import (Updater, Filters, MessageHandler)


class Converter:
    def __init__(self, update):
        self.update = update

    def valid_caption(self):
        return [el for el in self.update.channel_post.caption.strip().split("\n") if el]

    def file_name(self):
        return "{}.csv".format(uuid.uuid4())

    def run(self):
        self.valid_caption()

        with open(self.file_name(), 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([])
        return True

def receive_message(_, update):
    if update.channel_post.chat_id == settings.CHAT_ID:
        return Converter(update).run()


def run():
    messageHandler = MessageHandler(Filters.all, receive_message)
    updater = Updater(token = "622215110:AAGdb_eQSUFMvf52Vxz_UFfAV9w0fOcEKr4", request_kwargs={'read_timeout': 10, 'connect_timeout': 10})
    updater.dispatcher.add_handler(messageHandler)
    updater.start_polling()
