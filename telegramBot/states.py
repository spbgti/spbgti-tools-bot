# -*- coding: utf-8 -*-
import json
import requests
import random
import telepot
from spbgtitoolsbot import settings
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
TelegramBot = telepot.Bot(settings.TOKEN)


class State:
    possible_response = []  # возможные результаты ответа (если есть)
    error_messages = [
        {
            "type": "text",
            "text": "Произошла ошибка!"
         },
    ]  # сообщения об ошибках
    start_messages = []  # начальные сообщения

    @classmethod
    def send_message(cls, msg, chat_id):
        if 'custom_keyboard' in msg:
            reply_markup = ReplyKeyboardMarkup(keyboard=[list(map(lambda x:  KeyboardButton(text=x), i)) for i in msg['custom_keyboard']], resize_keyboard=True, one_time_keyboard=True)
        else:
            reply_markup = None

        if msg['type'] == 'text':
            TelegramBot.sendMessage(chat_id, msg['text'], reply_markup=reply_markup)

        return msg
        # реализовать универсальную функцию для отправки сообщений, возможно реализовать объект Message

    def start(self, chat_id, user):
        if len(self.start_messages) > 0:
            self.send_message(random.choice(self.start_messages), chat_id)

    def handler(self, user_msg, user):
        pass


class StartCommand(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Привет, это наш телеграм бот, и мы очень рады видеть тебя здесь! \n'
                    'По всем вопросам и предложениям пиши @b0g3r или @anamahpro, они будут рады тебя выслушать \n'
                    'А сейчас мы попросим тебя ответить на несколько вопросов:',
        },
    ]
    def handler(self, user_msg, user):
        user.change_state(Registration())

class Registration(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Ты учишься у нас?',
            'custom_keyboard': [["Нет", "Да"]],
        },
    ]
    possible_response = ["нет", "да"]
    error_messages = [
        {
            'type': 'text',
            'text': 'Давай попробуем ещё раз:',
        },
        {
            'type': 'text',
            'text': 'Попробуй ещё раз:',
        },
    ]
    # start() наследуется от предка

    def handler(self, user_msg, user):
        chat_id = user_msg['chat']['id']

        if user_msg['text'].lower() == self.possible_response[0]:
            user.is_student = False
            user.change_state(RegistrationSuccess())

        elif user_msg['text'].lower() == self.possible_response[1]:
            user.is_student = True
            user.change_state(RegistrationSetGroup())#группа
        else:
            self.send_message(random.choice(self.error_messages), chat_id)  # отправляем ошибку
            user.change_state(self)  # замыкаем состояние
            return None

        user.save()

class RegistrationSuccess(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Ты абитуриент',

        },
        {
            'type': 'text',
            'text': 'Ты студент',
        },
    ]
    def start(self, chat_id, user):
        if user.is_student:
            self.send_message(self.start_messages[1], chat_id)
            user.change_state(Menu())
        else:
            self.send_message(self.start_messages[0], chat_id)
            user.change_state(SimpleMenu())

    def handler(self, user_msg, user):
        user.change_state(self)


class RegistrationSetGroup(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Введи номер группы',
        },
    ]
    error_messages = [
        {
            'type': 'text',
            'text': 'Давай попробуем ещё раз:',
        },
        {
            'type': 'text',
            'text': 'Может ещё разок попробуешь?:',
        },
    ]

    def handler(self, user_msg, user):
        chat_id = user_msg['chat']['id']

        if True:  # группа есть в базе
            user.change_state(Menu())

        user.save()
    pass


class SimpleMenu(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'У нас для тебя есть:',
            'custom_keyboard': [["Информация"]],
        },
    ]
    possible_response = ["информация"]
    error_messages = [
        {
            'type': 'text',
            'text': 'Давай попробуем ещё раз:',
        },
        {
            'type': 'text',
            'text': 'Может ещё разок попробуешь?:',
        },
    ]

    def handler(self, user_msg, user):
        chat_id = user_msg['chat']['id']
        if user_msg['text'].lower() == self.possible_response[0]:
            user.change_state(Information())
            user.is_student = False
        else:
            self.send_message(random.choice(self.error_messages), chat_id)
            user.change_state(self)
            return None



class Menu(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Выбирай:',
            'custom_keyboard': [["Информация", "Расписание"]],
        },
    ]
    possible_response = ["информация", "расписание"]
    error_messages = [
        {
            'type': 'text',
            'text': 'Давай попробуем ещё раз:',
        },
        {
            'type': 'text',
            'text': 'Может ещё разок попробуешь?:',
        },
    ]

    def handler(self, user_msg, user):
        chat_id = user_msg['chat']['id']

        if user_msg['text'].lower() == self.possible_response[0]:
            user.is_student = True
            user.change_state(Information())

        elif user_msg['text'].lower() == self.possible_response[1]:
            user.is_student = False
            user.change_state(Schedule())
        else:
            self.send_message(random.choice(self.error_messages), chat_id)
            user.change_state(self)
            return None

        user.save()

class Schedule(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Расписание',
            'custom_keyboard': [["Сегодня", "Завтра"],
                                ["Эта неделя", "Вся неделя"],
                                ["Назад"]
                                ],
        },
    ]
    possible_response = ["сегодня", "завтра", "эта неделя", "вся неделя", "назад"]
    error_messages = [
        {
            'type': 'text',
            'text': 'Давай попробуем ещё раз:',
        },
        {
            'type': 'text',
            'text': 'Попробуй еще раз:',
        },
    ]

    def handler(self, user_msg, user):
        chat_id = user_msg['chat']['id']
        user.is_student = True
        response = requests.get('http://127.0.0.1:8001/api/get_schedule_by_group/123/')
        print(response.json())
        if user_msg['text'].lower() == self.possible_response[0]:
            pass

        elif user_msg['text'].lower() == self.possible_response[1]:
            pass
            # завтра

        elif user_msg['text'].lower() == self.possible_response[2]:
            pass
            # эта неделя
        elif user_msg['text'].lower() == self.possible_response[3]:
            pass
            # вся неделя

        elif user_msg['text'].lower() == self.possible_response[4]:
            user.change_state(Menu())


        else:
            self.send_message(random.choice(self.error_messages), chat_id)
            user.change_state(self)
            return None

        user.save()

class Information(State):
        start_messages = [
            {
                'type': 'text',
                'text': 'Это информация о боте',
                'custom_keyboard': [["Назад"]],
            },
        ]
        possible_response = ["назад"]
        error_messages = [
            {
                'type': 'text',
                'text': 'Давай попробуем ещё раз:',
            },
            {
                'type': 'text',
                'text': 'Попробуй еще раз:',
            },
        ]

        def handler(self, user_msg, user):
            chat_id = user_msg['chat']['id']

            if user_msg['text'].lower() == self.possible_response:
                user.change_state(Menu())

            else:
                self.send_message(random.choice(self.error_messages), chat_id)
                user.change_state(self)
                return None

            user.save()


