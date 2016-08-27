import json
import os

import telepot
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from bot.log_helpers import log_with_args
from bot.log_helpers import logger
from spbgtitoolsbot import settings
from telegramBot.models import User

TelegramBot = telepot.Bot(settings.TOKEN)


@csrf_exempt
@log_with_args
def webhook(request):
    msg = request.body.decode('utf-8')
    try:
        payload = json.loads(msg)
    except ValueError:
        logger.warning("Invalid request body")
        return HttpResponseBadRequest('Invalid request body')
    else:
        handle(payload['message'])
        return JsonResponse({}, status=200)


def start():
    if 'LOCAL' in os.environ.keys() and os.environ['LOCAL'] == 'YES':
        logger.info("запускаю longpoll")
        TelegramBot.setWebhook()  # disable webhook
        TelegramBot.message_loop(callback={'chat': handle})
    else:
        TelegramBot.setWebhook(url="https://spbgti-tools-bot.herokuapp.com/telegramBot/%s/" % settings.TOKEN)
    logger.info("Бот запущен")
    return True


@log_with_args
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    try:
        user = User.objects.get(telegram_id=msg['from']['id'])
    except User.DoesNotExist:
        user = User.create(telegram_id=msg['from']['id'])
    state = user.get_state()
    if state is None:
        logger.error("Error in state-field, user " + user.telegram_id)

    state.handler(msg, user)
