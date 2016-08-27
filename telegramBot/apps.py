from django.apps import AppConfig


class TelegrambotConfig(AppConfig):
    name = 'telegramBot'

    def ready(self):
        from bot import start
        start.start()
