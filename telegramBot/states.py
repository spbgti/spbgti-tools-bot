# -*- coding: utf-8 -*-
import logging

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
            try:
                bot.sendMessage(user.telegram_id, msg['text'], reply_markup=reply_markup)
            except Exception:
                logging.error('ERROR')
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
            'text': 'Привет, я - телеграм-бот для студентов техноложки, и я очень рад видеть тебя здесь!\n'
                    'Добро пожаловать в моё уютное гнездышко, полное удобств и расписаний\n'
                    'По всем вопросам и предложениям пиши @b0g3r, он будет рад тебя выслушать, исправить любые недочеты'
                    ' и записать твои пожелания\n'
                    'А сейчас пройди через небольшое интервью :)',
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
            'text': 'Впиши свою группу:'
        },
    ]

    @classmethod
    def handle(cls, user, user_msg):
        groups = [group['number'].lower() for group in requests.get(schedule_url+'/groups').json()]
        if user_msg.lower() in groups:
            user.group_number = user_msg.lower()
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
            'custom_keyboard': [["Информация", "Расписание", "Уведомления"],
                                ["Настройки"]],
        },
    ]
    possible_response = ["информация", "расписание", "уведомления", "настройки"]

    @classmethod
    def handle(cls, user, user_msg):
        if user_msg.lower() == cls.possible_response[0]:
            user.change_state(Info) #Инфо
        elif user_msg.lower() == cls.possible_response[1]:
            user.change_state(Schedule)
        elif user_msg.lower() == cls.possible_response[2]:
            user.change_state(NotificationMenu)
        elif user_msg.lower() == cls.possible_response[3]:
            user.change_state(Settings) # настройки
        else:
            cls.reset(user)


@state
class Schedule(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Выбери тип расписания (попробуй их все!):',
            'custom_keyboard': [["День", "Неделя", "Полное"],
                                ["Назад"]],
        },
    ]
    possible_response = ["день", "неделя", "полное", "назад"]

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


@state
class Info(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Я создан коллективом разработчиков из vk.com/code_spbgti, которым стало однажды скучно и захотелос'
                    'ь сделать мир лучше. Так появился я - маленький умный робот-помощник от студентов для студентов.'
                    ' Если отбросить все технические детали, то основная моя идеология - быть максимально открытым, '
                    'позволять другим творить и быть услышанным.\n'
                    'Я знаю расписание всех курсов 1-5 факультетов, в том числе магистратуры\n'
                    'Я умею выдавать его по запросу: полное, на эту/следующую неделю, на сегодня/завтра/три дня. Для '
                    'этого используй пункт меню "Расписание"\n'
                    'Я умею присылать каждое утро или каждый вечер расписание на день, чтобы ты знал что можно пропуст'
                    'ить :) Меню "Уведомления". Там же можно отключить эту функцию.\n'

                    'Но я всё ещё в стадии бета-теста, и только-только начал расти и развиваться. У меня есть проблемы,'
                    ' и никто их не поможет исправить кроме вас - моих любимых пользователей. Пишите обо всех недочетах'
                    ' @b0g3r или в сообщения паблику, я также нуждаюсь в твоих предложениях и идеях как мне развиваться'
                    ' дальше :)\n'
                    'У меня также есть задачи на будущее, которые постепенно будут реализовываться:\n'
                    '- Относительное время уведомлений (зачем тебя будить в 8, если тебе ко второй?)\n'
                    '- Расписание для ФЭМ\n'
                    '- Доступ к методичкам\n'
                    'Чтобы быть в курсе всех новых фишечек и изменений, подписывайся на мой новостной канал: '
                    '@news_spbgti_bot\n'
                    'Твой робот-помощник, @spbgti_bot'
        },
    ]

    @classmethod
    def set(cls, user):
        super().set(user)
        user.change_state(Menu)


@state
class Settings(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Настройки',
            'custom_keyboard': [["Группа"],
                                ["Назад"]],
        },
    ]
    possible_response = ["группа", "назад"]

    @classmethod
    def handle(cls, user, user_msg):
        if user_msg.lower() == cls.possible_response[0]:
            user.change_state(SettingGroup)
        elif user_msg.lower() == cls.possible_response[1]:
            user.change_state(Menu)
        else:
            cls.reset(user)


@state
class NotificationMenu(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Хочешь, чтобы я сам присылал тебе расписание? Я могу присылать каждое утро расписание на новый'
                    ' день, либо каждый вечер расписание на следующий день. А могу вообще не присылать :(',
            'custom_keyboard': [["Утром", "Вечером", "Не хочу"],
                                ["Назад"]],
        },
    ]
    possible_response = ["утром", "вечером", "не хочу", "назад"]

    @classmethod
    def handle(cls, user, user_msg):
        if user_msg.lower() == cls.possible_response[0]:
            user.change_state(SettingMorningNotification)
        elif user_msg.lower() == cls.possible_response[1]:
            user.change_state(SettingEveningNotification)
        elif user_msg.lower() == cls.possible_response[2]:
            user.notification_time = ''
            user.change_state(Menu)
        elif user_msg.lower() == cls.possible_response[3]:
            user.change_state(Menu)
        else:
            cls.reset(user)


@state
class SettingMorningNotification(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Выбери удобное для тебя время:',
            'custom_keyboard': [["7:00", "7:30", "8:00"],
                                ["Назад"]],
        },
    ]
    possible_response = ["7:00", "7:30", "8:00", "назад"]

    @classmethod
    def handle(cls, user, user_msg):
        if user_msg.lower() in cls.possible_response:
            if user_msg.lower() == cls.possible_response[3]:
                user.change_state(NotificationMenu)
            else:
                user.notification_time = user_msg
                user.change_state(Menu)
        else:
            cls.reset(user)


@state
class SettingEveningNotification(_State):
    start_messages = [
        {
            'type': 'text',
            'text': 'Выбери удобное для тебя время:',
            'custom_keyboard': [["20:00", "21:00", "22:00", "23:00"],
                                ["Назад"]],
        },
    ]
    possible_response = ["20:00", "21:00", "22:00", "23:00", "назад"]

    @classmethod
    def handle(cls, user, user_msg):
        if user_msg.lower() in cls.possible_response:
            if user_msg.lower() == cls.possible_response[4]:
                user.change_state(NotificationMenu)
            else:
                user.notification_time = user_msg
                user.change_state(Menu)
        else:
            cls.reset(user)