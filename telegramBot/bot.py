#! /usr/bin/env python
# -*- coding: utf-8 -*-


from datetime import datetime
import telepot
from spbgtitoolsbot import settings
import os
from django.http import JsonResponse
import json

def webhook(request, token):
    if token != settings.TOKEN:
        newlog("Запрос на запуск бота с неправильным токеном")
        return JsonResponse({}, status=200)
    msg = request.body.decode('utf-8')
    try:
        payload = json.loads(msg)
    except ValueError:
        return newlog("Получено неправильное сообщение")
    else:
        handle(payload)

def start():
    global TelegramBot
    TelegramBot = telepot.Bot(settings.TOKEN)
    if "LOCAL" in os.environ.keys():
        TelegramBot.message_loop(handle)
    else:
        TelegramBot.setWebhook(url="https://spbgti-tools-bot.herokuapp.com/telegramBot/%s" % settings.TOKEN)
    newlog("старт")
    return True

def newlog(*args):
    filelog = open("telegramBot/log.txt", "a")
    now=datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    filelog.write(now+" "+' '.join(args)+"\n")
    filelog.close()
    return True


def handle(msg):
    newlog(str(msg))
    if 'text' in msg.keys:
        pass #это текстовое сообщение
    else:
        pass #это какое-то другое сообщение
    '''
    if msg["text"] == "/start":
        command_start(msg)
    '''
def command_start(msg):
    template_file = open("templates/commandstart.txt", "r")
    TelegramBot.sendMessage(msg["chat"]["id"],template_file.read())
    template_file.close()




"""
import telebot
token = "TOKEN"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["help"])
def handle_text(message):
    bot.send_message(message.chat.id, "Мои возможности")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "a":
        bot.send_message(message.chat.id, "b")
    elif message.text == "b":
        bot.send.message(message.chat.id, "a")



bot.polling(none_stop=True, interval = 0)

############################################################################################

import requests
import telebot
from telebot import types
from telebot import util

logger = telebot.logger
CONNECT_TIMEOUT = 3.5
READ_TIMEOUT = 9999
def _make_request(token, method_name, method='get', params=None, files=None, base_url=API_URL):
    """

"""
    request_url = base_url.format(token, method_name)
    logger.debug("Request: method={0} url={1} params={2} files={3}".format(method, request_url, params, files))
    read_timeout = READ_TIMEOUT
    connect_timeout = CONNECT_TIMEOUT
    if params:
        if 'timeout' in params: read_timeout = params['timeout'] + 10
        if 'connect-timeout' in params: connect_timeout = params['connect-timeout'] + 10
    result = requests.request(method, request_url, params=params, files=files, timeout=(connect_timeout, read_timeout))
    logger.debug("The server returned: '{0}'".format(result.text.encode('utf8')))
    return _check_result(method_name, result)['result']

"""
"""import urllib
import json
import time

API = 'https://api.telegram.org/bot'
TOKEN = '261615304:AAHn-Vn9FpVkpfJxpx7RE00AYfRIii8v8zk'

URL = API + TOKEN
INVALID_UPDATE_ID = 0

def getUpdates():
    get = URL + '/getUpdates'
    response = urllib.urlopen(get)
    return response.read()

def getCommand():
    js = json.loads(getUpdates())

    update_obj = js['result'][-1]

    global last_update_id
    if last_update_id == INVALID_UPDATE_ID:
        last_update_id = update_obj['update_id']
        return None

    if update_obj['update_id'] != last_update_id:
        last_update_id = update_obj['update_id']
        return update_obj['message']['text']
    return None

while True:
    command = getCommand()

time.sleep(1)
"""




