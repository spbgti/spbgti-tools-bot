from django.apps import AppConfig
import os

class TelegrambotConfig(AppConfig):
    name = 'telegramBot'

    def ready(self):
        from . import bot
        bot.start()