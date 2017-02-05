# -*- coding: utf-8 -*-
from spbgtitoolsbot import settings
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from .callbacks import callbacks
import requests
import random
import telepot

bot = telepot.Bot(settings.TOKEN)
schedule_url = settings.SCHEDULE_API
states = {}

def state(cls):
    states[cls.__name__] = cls
    return cls

class _State:
    """
    Base State
    """
    start_messages = [
        {
            'type': 'text',
            'text': 'Стартовое сообщение'
        },
        {
            'type': 'text',
            'text': 'Привет!'
        }
    ]
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
    @classmethod
    def send_message(cls, msg, user):
        """
        Send message to user
        :type msg: dict
        :type user: models.User
        :return:
        """
        if 'custom_keyboard' in msg:
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[list(map(lambda x: KeyboardButton(text=x), i)) for i in msg['custom_keyboard']],
                resize_keyboard=True, one_time_keyboard=True)
        elif 'inline_keyboard' in msg:
            reply_markup = msg['inline_keyboard']
        else:
            reply_markup = None

        if msg['type'] == 'text':
            bot.sendMessage(user.telegram_id, msg['text'], reply_markup=reply_markup)

        return msg
        # реализовать универсальную функцию для отправки сообщений, возможно реализовать объект Message

    @classmethod
    def set(cls, user):
        """
        Called when set this state to user
        :type user: models.User
        """
        cls.send_message(random.choice(cls.start_messages), user)

    @classmethod
    def reset(cls, user):
        """
        Send error to user and reset this state
        :type user: models.User
        """
        cls.send_message(random.choice(cls.error_messages), user)
        user.change_state(cls)

    @classmethod
    def handle(cls, user, user_msg):
        """
        Handles the received message
        :type user: models.User
        :type user_msg: str
        """

@state
class Start(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Привет, это наш телеграм бот, и мы очень рады видеть тебя здесь! \n'
                    'По всем вопросам и предложениям пиши @b0g3r или @anamahpro, они будут рады тебя выслушать \n'
                    'А сейчас мы попросим тебя ответить на несколько вопросов:',
        },
    ]

    @classmethod
    def set(cls, user):
        cls.send_message(cls.start_messages[0], user)
        user.change_state(SettingGroup)


@state
class SettingTypeEducation(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Ты ...',
            'custom_keyboard': [["Абитуриент", "Студент"]],
        },
    ]
    possible_response = ["абитуриент", "студент"]

    @classmethod
    def handle(cls, user, user_msg):
        if user_msg.lower() == cls.possible_response[0]:
            user.is_student = False
            user.change_state(Menu)
        elif user_msg.lower() == cls.possible_response[1]:
            user.is_student = True
            user.change_state(SettingGroup)
        else:
            cls.reset(user)


@state
class SettingGroup(_State):
    error_messages = [
        {
            'type': 'text',
            'text': 'Мы не смогли найти твою группу, попробуй ещё раз!'
        }
    ]
    start_messages = [
        {
            'type': 'text',
            'text': 'Впиши свою группу'
        },
    ]

    @classmethod
    def handle(cls, user, user_msg):
        groups = [group['number'] for group in requests.get(schedule_url+'/groups').json()]
        if user_msg.upper() in groups:
            user.group_number = user_msg
            user.change_state(Menu)
        else:
            groups = [group for group in groups if group.startswith(user_msg[:3])]
            if groups:
                cls.send_message({'type': 'text',
                                  'text': 'Может быть что-то из этих?',
                                  'custom_keyboard': [[group] for group in groups]},
                                 user)
                user.change_state(cls, silent=True)
            else:
                cls.reset(user)


@state
class Menu(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Меню:',
            'custom_keyboard': [["Информация", "Расписание", "Настройки"]],
        },
    ]
    possible_response = ["информация", "расписание", "настройки"]

    @classmethod
    def handle(cls, user, user_msg):
        if user_msg.lower() == cls.possible_response[0]:
            user.change_state() #Инфо
        elif user_msg.lower() == cls.possible_response[1]:
            user.change_state(Schedule)
        elif user_msg.lower() == cls.possible_response[2]:
            user.change_state() # настройки
        else:
            cls.reset(user)

@state
class Schedule(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Выбери тип расписания (попробуй их все!):',
            'custom_keyboard': [["На день", "На неделю", "Полное", "Назад"]],
        },
    ]
    possible_response = ["на день", "на неделю", "полное", "назад"]

    @classmethod
    def handle(cls, user, user_msg):
        if user_msg.lower() == cls.possible_response[3]:
            user.change_state(Menu)
            return
        if user_msg.lower() in cls.possible_response:
            if user_msg.lower() == cls.possible_response[0]:
                text, keyboard = callbacks['DayScheduleCallback'].init_message()
            elif user_msg.lower() == cls.possible_response[1]:
                text, keyboard = callbacks['WeekScheduleCallback'].init_message()
            else:
                text, keyboard = callbacks['AllScheduleCallback'].init_message()
            cls.send_message({'type': 'text', 'text': text, 'inline_keyboard': keyboard}, user)
            user.change_state(Schedule)
        else:
            cls.reset(user)


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
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[list(map(lambda x: KeyboardButton(text=x), i)) for i in msg['custom_keyboard']],
                resize_keyboard=True, one_time_keyboard=True)
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
            user.change_state(RegistrationSetGroup()) # группа
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



class _Menu(State):
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

class _Schedule(State):
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


