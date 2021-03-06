import telepot
from spbgtitoolsbot import settings
import os
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.views.decorators.csrf import csrf_exempt
import logging
from .models import User
from .callbacks import callbacks
logger = logging.getLogger("telegramBot")

bot = telepot.Bot(settings.TOKEN)


@csrf_exempt
def webhook(request):
    msg = request.body.decode('utf-8')
    logger.info("Message received from webhook from " + request.META.get('REMOTE_ADDR', None))
    try:
        payload = json.loads(msg)
    except ValueError:
        logger.warning("Invalid request body")
        return HttpResponseBadRequest('Invalid request body')
    else:
        query = payload.get('message') or payload.get('callback_query')
        handle(query)
        return JsonResponse({}, status=200)


def start():
    if 'LOCAL' in os.environ.keys() and os.environ['LOCAL'] == 'YES':
        newlog("запускаю longpoll")
        bot.deleteWebhook()
        bot.message_loop(handle)
    else:
        url = "{}/telegramBot/{}/".format(settings.SERVER_URL, settings.TOKEN)
        if bot.getWebhookInfo()['url'] != url:
            bot.setWebhook(url=url)
    newlog("Бот запущен")
    return True


def newlog(*args):
    for arg in args:
        logger.info(arg)
    return True


def handle(msg):
    if telepot.flavor(msg) == 'callback_query':
        logger.info("Callback query processing:")
        logger.info(msg)
        logger.info(' by ' + str(msg['from']['id']))
        user = User.objects.get(telegram_id=msg['from']['id'])
        callbacks[msg['data'].split('_')[0]].handle(msg, user)
    elif telepot.flavor(msg) == 'chat' and telepot.glance(msg)[0] == 'text':
        content_type, chat_type, chat_id = telepot.glance(msg)
        logger.info("Message processing:")
        logger.info(msg)
        logger.info(content_type + ' by ' + str(msg['from']['id']))
        try:
            user = User.objects.get(telegram_id=msg['from']['id'])
        except User.DoesNotExist:
            User.create(telegram_id=msg['from']['id'])
        else:
            user.get_state().handle(user, msg['text'])