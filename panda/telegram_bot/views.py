import csv
import uuid

from django.conf import settings
from telegram.ext import (Updater, Filters, MessageHandler)


class Converter:
    def __init__(self, update):
        self.update = update

    def file_name(self):
        return "{}.csv".format(uuid.uuid4())

    def write(self):
        with open(self.file_name(), 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([])
        return True

    def run(self):
        self.valid_caption()
        return self.write()

def receive_message(_, update):
    if update.channel_post.chat_id == settings.CHAT_ID:
        return Converter(update).run()

def run():
    messageHandler = MessageHandler(Filters.all, receive_message)
    updater = Updater(
        token = settings.TOKEN_TELEGRAM,
        request_kwargs={'read_timeout': 10, 'connect_timeout': 10}
    )
    updater.dispatcher.add_handler(messageHandler)
    updater.start_webhook(
        listen = '0.0.0.0',
        port = 443,
        url_path = settings.TOKEN_TELEGRAM
    )
    updater.bot.set_webhook(
        webhook_url='https://{}:{}/{}'.format("176.36.12.87", 443, settings.TOKEN_TELEGRAM),
        certificate = open('cert.pem', 'rb')
    )
    # updater.start_webhook(
    #     listen='0.0.0.0',
    #     port=443,
    #     url_path=settings.TOKEN_TELEGRAM,
    #     key='private.key',
    #     cert='cert.pem',
    #     webhook_url='https://{}:{}/{}'.format("176.36.12.87", 443, settings.TOKEN_TELEGRAM)
    # )

if __name__ == "__main__":
    run()

