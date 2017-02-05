from django.core.management.base import BaseCommand, CommandError
from telepot import Bot
from spbgtitoolsbot.settings import TOKEN
from telegramBot.models import User
from telegramBot.callbacks import DayScheduleCallback
from datetime import date

bot = Bot(TOKEN)


class Command(BaseCommand):
    help = 'Send notifications'

    def add_arguments(self, parser):
        parser.add_argument('time', type=str)

    def handle(self, *args, **options):
        if options['time']:
            time = options['time']
            for mapping in User.times:
                if mapping[1] == time:
                    time_db_value = mapping[0]
                    break
            else:
                raise CommandError('Unknown time')

            for user in User.objects.filter(notification_time=time_db_value):
                message = DayScheduleCallback.generate_message_for_day(user.group_number, date.today())
                bot.sendMessage(chat_id=user.telegram_id, text=message)