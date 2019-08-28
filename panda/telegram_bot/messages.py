from telegram.ext import (Updater,Filters,MessageHandler)
from django.conf import settings
import csv


def valid_caption(caption):
    return [el for el in caption.strip().split("\n") if el]

def receive_message(_, update):
    if update.channel_post.chat_id == settings.CHAT_ID:
        valid_caption(update.channel_post.caption)

        with open('product.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([])
        return True

def run():
    messageHandler = MessageHandler(Filters.all, receive_message)
    updater = Updater(token = "622215110:AAGdb_eQSUFMvf52Vxz_UFfAV9w0fOcEKr4", request_kwargs={'read_timeout': 10, 'connect_timeout': 10})
    updater.dispatcher.add_handler(messageHandler)
    updater.start_polling()
