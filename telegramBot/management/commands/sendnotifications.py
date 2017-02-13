from django.core.management.base import BaseCommand, CommandError
from telepot import Bot
from spbgtitoolsbot.settings import TOKEN
from telegramBot.models import User
from telegramBot.callbacks import DayScheduleCallback
from datetime import date, timedelta

bot = Bot(TOKEN)


class Command(BaseCommand):
    help = 'Sends notifications'

    def add_arguments(self, parser):
        parser.add_argument('time', type=str)

    def handle(self, *args, time, **options):
        if time in ('7:00', '7:30', '8:00'):
            day = date.today()
        elif time in ('20:00', '21:00', '22:00', '23:00'):
            day = date.today()+timedelta(days=1)
        else:
            raise CommandError('wrong notification time')
        for user in User.objects.filter(notification_time=time):
            message = DayScheduleCallback.generate_message_for_day(user.group_number, day)
            bot.sendMessage(chat_id=user.telegram_id, text=message)
