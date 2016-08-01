# -*- coding: utf-8 -*-

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

    @staticmethod
    def send_message(msg, chat_id):
        if 'custom_keyboard' in msg:
            reply_markup = ReplyKeyboardMarkup(keyboard=[list(map(lambda x:  KeyboardButton(text=x), i)) for i in msg['custom_keyboard']], resize_keyboard=True, one_time_keyboard=True)
        else:
            reply_markup = None

        if msg['type'] == 'text':
            TelegramBot.sendMessage(chat_id, msg['text'], reply_markup=reply_markup)
        # реализовать универсальную функцию для отправки сообщений, возможно реализовать объект Message

    def start(self, chat_id):
        if len(self.start_messages) > 0:
            self.send_message(random.choice(self.start_messages), chat_id)

    def handler(self, user_msg, user):
        pass


class StartCommandState(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Привет, это наш телеграм бот, и мы очень рады видеть тебя здесь! \n'
                    'По всем вопросам и предложениям пиши @b0g3r или @anamahpro, они будут рады тебя выслушать \n'
                    'А сейчас мы попросим тебя ответить на несколько вопросов:',
        },
    ]
    def handler(self, user_msg, user):
        user.change_state(RegistrationState())

class RegistrationState(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Ты учишься у нас?',
            'custom_keyboard': [["Да", "Нет"]],
        },
    ]
    possible_response = ["да", "нет"]
    error_messages = [
        {
            'type': 'text',
            'text': 'Давай попробуем ещё раз:',
        },
        {
            'type': 'text',
            'text': 'Ты лошок, давай ещё:',
        },
    ]
    # start() наследуется от предка

    def handler(self, user_msg, user):
        chat_id = user_msg['chat']['id']

        if user_msg['text'].lower() == self.possible_response[0]:
            user.is_student = True
            user.change_state(Menu())

        elif user_msg['text'].lower() == self.possible_response[1]:
            user.is_student = False
        else:
            self.send_message(random.choice(self.error_messages), chat_id)  # отправляем ошибку
            user.change_state(self)  # замыкаем состояние
            return None

        user.save()

class Menu(State):
    start_messages = [
        {
            'type': 'text',
            'text': 'У нас отличное меню. Выбирай.',
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
            user.change_state(Schedule_students())
        else:
            self.send_message(random.choice(self.error_messages), chat_id)  # отправляем ошибку
            user.change_state(self)  # замыкаем состояние
            return None

        user.save()

class Schedule_students(State):
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

        if user_msg['text'].lower() == self.possible_response[0]:
            user.is_student = True
            # сегодня

        elif user_msg['text'].lower() == self.possible_response[1]:
            user.is_student = False
            # завтра

        elif user_msg['text'].lower() == self.possible_response[2]:
            user.is_student = False
            # эта неделя

        elif user_msg['text'].lower() == self.possible_response[3]:
            user.is_student = False
            # вся неделя

        elif user_msg['text'].lower() == self.possible_response[4]:
            user.is_student = False
            # назад

        else:
            self.send_message(random.choice(self.error_messages), chat_id)  # отправляем ошибку
            user.change_state(self)  # замыкаем состояние
            return None

        user.save()

class Information(State):
        start_messages = [
            {
                'type': 'text',
                'text': 'Это информация о боте',
                'custom_keyboard': ["Назад"],
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

            if user_msg['text'].lower() == self.possible_response[0]:
                user.is_student = True


            else:
                self.send_message(random.choice(self.error_messages), chat_id)  # отправляем ошибку
                user.change_state(self)  # замыкаем состояние
                return None

            user.save()


