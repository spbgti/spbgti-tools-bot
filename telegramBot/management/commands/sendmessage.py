from django.core.management.base import BaseCommand, CommandError
from telepot import Bot
from spbgtitoolsbot.settings import TOKEN
from telegramBot.models import User

bot = Bot(TOKEN)


class Command(BaseCommand):
    help = 'Sends message to telegram-user'

    def add_arguments(self, parser):
        parser.add_argument('telegram_id', type=str)
        parser.add_argument('msg', type=str)

    def handle(self, *args, telegram_id, msg, **options):
        try:
            pass#User.objects.get()
        except:
            pass