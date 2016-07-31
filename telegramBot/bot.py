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

logger = logging.getLogger("telegramBot")

TelegramBot = telepot.Bot(settings.TOKEN)

@csrf_exempt
def webhook(request, token):
    if token != settings.TOKEN:
        logger.warning("Invalide token")
        return HttpResponseForbidden('Invalid token')
    msg = request.body.decode('utf-8')
    logger.info("Message received from webhook:")
    logger.info(msg)
    logger.info("from " + request.META['REMOTE_ADDR'] + " " + request.META['REMOTE_HOST'])
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
        newlog("запускаю longpoll")
        TelegramBot.setWebhook() # disable webhook
        TelegramBot.message_loop(handle) #1
        #TelegramBot.message_loop({'inline_query': on_inline_query,
         #                 'chosen_inline_result': on_chosen_inline_result},
         #                       )
        #TelegramBot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query}) #2
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
    logger.info(content_type + ' by ' + str(msg['from']['id']))
    if content_type == 'text':
        text_handler(msg)  # это текстовое сообщение
        re_text(msg)
    elif content_type == 'sticker':
        sticker_handler(msg)
    elif content_type == 'document':
        document_handler(msg)
    elif content_type == 'location':
        location_handler(msg)
    else:
        other_handler(msg)


def text_handler(msg):
    if msg["text"] == "/start":
        command_start(msg)
    if msg["text"] == "/info":
        command_info(msg)


def command_start(msg):
    template_file = open("templates/commandstart.txt", "r")
    TelegramBot.sendMessage(msg["chat"]["id"],template_file.read())
    template_file.close()


def command_info(msg):
    template_file = open("templates/commandinfo.txt", "r")
    TelegramBot.sendMessage(msg["chat"]["id"], template_file.read())
    template_file.close()


def document_handler(msg):
    template_file = open("templates/document.txt", "r")
    TelegramBot.sendMessage(msg["chat"]["id"], template_file.read())
    template_file.close()


def sticker_handler(msg):
    template_file = open("templates/sticker.txt", "r")
    TelegramBot.sendMessage(msg["chat"]["id"], template_file.read())
    template_file.close()


def location_handler(msg):
    template_file = open("templates/location.txt", "r")
    TelegramBot.sendMessage(msg["chat"]["id"], template_file.read())
    template_file.close()


def other_handler(msg):
    template_file = open("templates/other.txt", "r")
    TelegramBot.sendMessage(msg["chat"]["id"], template_file.read())
    template_file.close()


def re_text(msg):
    result = re.findall("спасиб", str(msg))
    if result:
        template_file = (open("templates/thanks_answers.txt", "r").read().splitlines())
        line = random.choice(template_file)
        TelegramBot.sendMessage(msg["chat"]["id"], line)
        template_file.close()



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





