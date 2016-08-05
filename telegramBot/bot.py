#! /usr/bin/env python
# -*- coding: utf-8 -*-

import telepot
from spbgtitoolsbot import settings
import os
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
import json
from django.views.decorators.csrf import csrf_exempt
import logging
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from telepot.delegate import per_chat_id, create_open
import sys
import re
import random
from .models import User
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
logger = logging.getLogger("telegramBot")

TelegramBot = telepot.Bot(settings.TOKEN)
update_queue = Queue()

@csrf_exempt
def webhook(request, token):
    if token != settings.TOKEN:
        logger.warning("Invalide token")
        return HttpResponseForbidden('Invalid token')
    msg = request.body.decode('utf-8')
    logger.info("Message received from webhook from " + request.META.get('REMOTE_ADDR', None))
    update_queue.put(msg)
    return JsonResponse({}, status=200)
    # TODO: сделать очередь


def start():
    if 'LOCAL' in os.environ.keys() and os.environ['LOCAL'] == 'YES':
        newlog("запускаю longpoll")
        TelegramBot.setWebhook() # disable webhook
        TelegramBot.message_loop(callback={'chat': handle}) #1
    else:
        TelegramBot.setWebhook(url="https://spbgti-tools-bot.herokuapp.com/telegramBot/%s/" % settings.TOKEN)
    newlog("Бот запущен")
    return True


def newlog(*args):
    for arg in args:
        logger.info(arg)

    return True


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    logger.info("Message processing:")
    logger.info(msg)
    logger.info(content_type + ' by ' + str(msg['from']['id']))
    try:
        user = User.objects.get(telegram_id=msg['from']['id'])
    except User.DoesNotExist:
        user = User.create(telegram_id=msg['from']['id'])
    state = user.get_state()
    if state is None:
        logger.error("Error in state-field, user " + user.telegram_id)

    state.handler(msg, user)


'''


def on_chat_message(msg):  # для 2 (callback_query)
    content_type, chat_type, chat_id = telepot.glance(msg)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Press me', callback_data='press')],
               ])

    TelegramBot.editMessageText(chat_id, 'Use inline keyboard', reply_markup=keyboard)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

    TelegramBot.answerCallbackQuery(query_id, text='Got it!')





'''