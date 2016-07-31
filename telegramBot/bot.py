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
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import sys
import re
import random
import json

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
    logger.info("from " + request.META.REMOTE_ADDR + " " + request.META.REMOTE_HOST)
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
        TelegramBot.message_loop(handle)
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
    elif msg["text"] == "/info":
        command_info(msg)
    else:
        eval(temp_get_state(msg))(msg)


def temp_get_state(msg):
    with open('telegramBot/temp.json', 'r') as f:
        data = json.loads(f.read())
    if not msg["from"]["id"] in data['data'].keys():
        data['data'][msg["from"]["id"]] = "registration"
    return data['data'][msg['from']['id']]


def temp_set_state(msg, state):
    with open('telegramBot/temp.json', 'r') as f:
        data = json.loads(f.read())
    print(data)
    data['data'][msg["from"]["id"]] = state.__name__
    with open('telegramBot/temp.json', 'w') as f:
        f.write(json.dumps(data))


def command_start(msg):
    registration(msg)
    template_file = open("templates/commandstart.txt", "r")
    TelegramBot.sendMessage(msg["chat"]["id"], template_file.read())

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


def registration(msg):
    temp_set_state(msg,registration_set_faculty)
    TelegramBot.sendMessage(msg["chat"]["id"], 'Регистрация. Я ...',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Студент"), KeyboardButton(text="Магистрант"), KeyboardButton(text="СПО")]
                                ], resize_keyboard=True
                            ))


# если студент (бакалавриат, потом учесть специалитет и очное, заочное)
def registration_set_faculty(msg):
    TelegramBot.sendMessage(msg["chat"]["id"], 'Выбери факультет',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="1 ф"),
                                     KeyboardButton(text="2 ф"),
                                     KeyboardButton(text="3 ф"),
                                     KeyboardButton(text="4 ф"),
                                     KeyboardButton(text="5 ф"),
                                     KeyboardButton(text="6 ф"),
                                     ]
                                ], resize_keyboard=True
                            ))


def registration_set_stage(msg):
    TelegramBot.sendMessage(msg["chat"]["id"], 'Выбери уровень образования',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Бакалавриат"), KeyboardButton(text="Специалитет"),]
                                ], resize_keyboard=True
                            ))



def registration_set_year_student(msg):
    TelegramBot.sendMessage(msg["chat"]["id"], 'Выбери год поступления',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="2016"),
                                     KeyboardButton(text="2015"),
                                     KeyboardButton(text="2014"),
                                     KeyboardButton(text="2013"),
                                     KeyboardButton(text="2012"),
                                     ]
                                ], resize_keyboard=True
                            ))

def registration_set_group_student(msg):
    TelegramBot.sendMessage(msg["chat"]["id"], 'Выбери группу',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="1"),
                                     KeyboardButton(text="2"),
                                     KeyboardButton(text="3"),
                                     KeyboardButton(text="4"),
                                     KeyboardButton(text="5"),
                                     KeyboardButton(text="6"),
                                     ]
                                ], resize_keyboard=True
                            ))


# если магистрант
def registration_set_faculty_undergraduate(msg):
    TelegramBot.sendMessage(msg["chat"]["id"], 'Выбери год поступления',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="2012"),
                                     KeyboardButton(text="2011"),
                                     ]
                                ], resize_keyboard=True
                            ))

# СПО оставим пока
# запомнили номер группы
# переходим в меню


def menu(msg):
    TelegramBot.sendMessage(msg["chat"]["id"], 'Меню',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Информация"),
                                     KeyboardButton(text="Расписание"),
                                     ]
                                ], resize_keyboard=True
                            ))


def schedule_students(msg):
    TelegramBot.sendMessage(msg["chat"]["id"], 'Меню',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Сегодня"), KeyboardButton(text="Завтра"),
                                     KeyboardButton(text="Эта неделя"), KeyboardButton(text="Всё расписание"),
                                     ]
                                ], resize_keyboard=True
                            ))









