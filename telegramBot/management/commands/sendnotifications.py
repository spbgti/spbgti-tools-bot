from django.core.management.base import BaseCommand, CommandError
from telepot import Bot
from spbgtitoolsbot.settings import TOKEN
from telegramBot.models import User
from telegramBot.callbacks import DayScheduleCallback
from datetime import date, timedelta
import logging

bot = Bot(TOKEN)

logger = logging.getLogger("telegramBot")


class Command(BaseCommand):
    help = 'Sends notifications'

    def add_arguments(self, parser):
        parser.add_argument('time', type=str)

    def handle(self, *args, time, **options):
        if time in ('7:00', '7:30', '8:00'):
            day_date = date.today()
        elif time in ('20:00', '21:00', '22:00', '23:00'):
            day_date = date.today()+timedelta(days=1)
        else:
            raise CommandError('wrong notification time')

        if day_date.isoweekday() > 5:
            logger.info("No exercises today")
            return
        for user in User.objects.filter(notification_time=time):
            message = DayScheduleCallback.generate_message_for_day(user.group_number, day_date)
            if message.count('--') == 4:  # no one exercise in the day
                logger.info("No exercises today for {}".format(user.telegram_id))
            else:
                try:
                    bot.sendMessage(chat_id=user.telegram_id, text=message, parse_mode='markdown')
                except Exception:
                    logging.error('ERROR')
                logger.info("Send notification {} to {}".format(time, user.telegram_id))
