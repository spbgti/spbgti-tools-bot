import json
import logging

from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import telepot
from spbgtitoolsbot.settings import TOKEN
from datetime import date, timedelta
from copy import deepcopy
from . import scheduleapi

bot = telepot.Bot(TOKEN)
callbacks = {}


def callback(cls):
    callbacks[cls.__name__] = cls
    return cls


class InlineKeyboardCallback:
    """
    Базовый класс для обработки приходящих нажатий на инлайн-клавиатуру
    """
    keyboard = [
        [['button1', 'data1'], ['button2', 'data2']],
        [['button3', 'data3']]
    ]

    @classmethod
    def handle(cls, query, user):
        msg_id = (query['message']['chat']['id'], query['message']['message_id'])
        callback_id = query['id']
        group = user.group_number
        try:
            message = cls.dispatch(query, group, user)

            keyboard = cls.get_keyboard(query)

            cls.edit(msg_id, callback_id, message, keyboard)
        except Exception:
            logging.exception('error')

    @classmethod
    def get_keyboard(cls, query):
        """
        Возвращает инлайн-клавиатуру для передачи в telegram-api
        При необходимости выделяет кнопку
        :param query:
        :return:
        """
        raise NotImplementedError()

    @classmethod
    def dispatch(cls, query, group, user):
        """
        Возвращает сообщение в зависимости от нажатой кнопки
        """
        raise NotImplementedError()

    @classmethod
    def edit(cls, msg_id, callback_id, msg, keyboard):
        try:
            bot.editMessageText(msg_id, text=msg, reply_markup=keyboard, parse_mode='markdown')
        except telepot.exception.TelegramError:
            try:
                bot.answerCallbackQuery(callback_id, text='Уже нажато ;)')
            except telepot.exception.TelegramError:
                pass
        else:
            try:
                bot.answerCallbackQuery(callback_id)
            except telepot.exception.TelegramError:
                pass

    @classmethod
    def generate_inline_keyboard(cls, keyboard):
        l = [list(map(lambda x: InlineKeyboardButton(
            text=x[0], callback_data='{}_{}'.format(cls.__name__, x[1])), i)) for i in keyboard]
        return InlineKeyboardMarkup(inline_keyboard=l)

    @classmethod
    def init_message(cls):
        raise NotImplementedError()


class BaseScheduleCallback(InlineKeyboardCallback):
    days = ('🌑 Понедельник', '🌘 Вторник', '🌗 Среда',
            '🌖 Четверг', '🌕 Пятница', '🌝 Суббота', '🌚 Воскресенье')
    months = ('января', "февраля", "марта", "апреля", "мая", "июня",
              "июля", "августа", "сентября", "октября", "ноября", "декабря")
    times = ('09:30', '11:15', '13:30', '15:15')

    @classmethod
    def generate_exercise(cls, exercise, teachers_visible):
        return '*{name}* {type} {room} `{teachers}`'.format(
            name=exercise['name'],
            type='(' + exercise['type'] + ')' if exercise['type'] else '',
            room=scheduleapi.get_room(exercise['room_id']),
            teachers=', '.join(exercise['teachers'] if teachers_visible
                               else [])
        )

    @classmethod
    def generate_day_schedule(cls, day_schedule: list, teachers_visible):
        f_day_schedule = ''
        for pair in range(1, 5):
            exercise = " -- "
            for ex in day_schedule:
                if ex['pair'] == str(pair):
                    exercise = cls.generate_exercise(ex, teachers_visible)
            f_day_schedule += '`{}.` {}\n'.format(cls.times[pair-1], exercise)
        return f_day_schedule

@callback
class DayScheduleCallback(BaseScheduleCallback):
    keyboard = [[['Сегодня', 0], ['Завтра', 1]]]

    @classmethod
    def get_keyboard(cls, query):
        select = int(query['data'].split('_')[1])
        keyboard = deepcopy(cls.keyboard)
        keyboard[0][select][0] = '· {} ·'.format(keyboard[0][select][0])
        return cls.generate_inline_keyboard(keyboard)

    @classmethod
    def dispatch(cls, query, group, user):
        day = int(query['data'].split('_')[1])
        if day == 0:
            return cls.generate_message_for_day(group, user, date.today())
        elif day == 1:
            return cls.generate_message_for_day(group, user, date.today() +
                                                timedelta(days=1))
        else:
            return 'error!'

    @classmethod
    def generate_message_for_day(cls, group, user, day_date):
        schedule, weekday, parity = scheduleapi.get_date_schedule(group, day_date)
        schedule = [exercise for exercise in schedule if
                    exercise['day'] == str(weekday) and
                    (exercise['parity'] is None or exercise['parity'] == str(parity))]
        message = '{}, {} {} _({})_\n'.format(cls.days[weekday - 1],
                                              day_date.day,
                                              cls.months[day_date.month-1],
                                              "четн" if parity == 1 else 'нечетн')

        message += cls.generate_day_schedule(schedule, user.teachers_visible)
        return message

    @classmethod
    def init_message(cls):
        message = """Я сообщение-расписание. Жмякай на "Сегодня" или "Завтра" и я выдам тебе желанное расписание. """
        """Учти, что я работаю по питерскому времени и в полночь у меня начинается следующий день ;)"""
        keyboard = cls.generate_inline_keyboard(deepcopy(cls.keyboard))
        return message, keyboard


@callback
class WeekScheduleCallback(BaseScheduleCallback):
    keyboard = [[['Четная', 0], ['Нечетная', 1]]]

    @classmethod
    def get_keyboard(cls, query):
        select = int(query['data'].split('_')[1])
        keyboard = deepcopy(cls.keyboard)
        keyboard[0][select][0] = '· {} ·'.format(keyboard[0][select][0])
        return cls.generate_inline_keyboard(keyboard)

    @classmethod
    def dispatch(cls, query, group, user):
        week = int(query['data'].split('_')[1])
        if week == 0:
            return cls.generate_message_for_week(group, user, parity='1')
        elif week == 1:
            return cls.generate_message_for_week(group, user, parity='2')
        else:
            return 'error!'

    @classmethod
    def generate_message_for_week(cls, group, user, parity):
        message = 'Четная неделя\n' if parity == '1' else 'Нечетная неделя\n'
        for weekday in range(1, 6):
            try:
                day_schedule = scheduleapi.get_weekday_schedule(group, weekday, parity)

                message += '\n{}\n'.format(cls.days[weekday - 1])
                message += cls.generate_day_schedule(day_schedule, user.teachers_visible)
            except json.decoder.JSONDecodeError:
                return "Произошла ошибка. Похоже, что я не нашел твоей " \
                       "группы :(. Возможно чуть позже я смогу тебе помочь"
        return message

    @classmethod
    def init_message(cls):
        message = """Я сообщение-расписание по неделям. Жмякай на кнопки и получишь простыню текста. """
        """Учти, что при изменении в расписании сообщение само не обновится, поэтому при сомнениях - жмякай снова"""
        keyboard = cls.generate_inline_keyboard(deepcopy(cls.keyboard))
        return message, keyboard


@callback
class AllScheduleCallback(BaseScheduleCallback):
    """
    Клавиатура - к данным для всех кнопок прибавляем выбор по первой и второй строке
    К примеру если были выбрана четная неделя и понедельник, и была нажата кнопка "нечетная", то придет следующая data:
    AllScheduleCallback_1_0_2 (1 - нажатие, 0 и 2 - предыдущий выбор)
    По умолчанию выбор на четная-понедельник.
    """
    keyboard = [
        [['Четная', 0], ['Нечетная', 1]],
        [['Пон', 2], ['Вт', 3], ['Ср', 4], ['Чет', 5], ['Пят', 6]]
    ]

    @classmethod
    def dispatch(cls, query, group, user):
        button, first_row, second_row,  = map(int, query['data'].split('_')[1:])
        if 0 <= button <= 1:  # выбор четности
            parity = button + 1
            weekday = second_row - 1
        else:  # выбор дня недели
            parity = first_row + 1
            weekday = button - 1
        return cls.generate_message(group, user, parity, weekday)

    @classmethod
    def generate_message(cls, group, user, parity, weekday):
        schedule = scheduleapi.get_weekday_schedule(group, weekday, parity)
        message = '{}, _({})_\n'.format(cls.days[weekday - 1],
                                      "четн" if parity == 1 else 'нечетн')

        message += cls.generate_day_schedule(schedule, user.teachers_visible)
        return message

    @classmethod
    def get_keyboard(cls, query):
        keyboard = deepcopy(cls.keyboard)
        button, first_row, second_row,  = map(int, query['data'].split('_')[1:])

        if 0 <= button <= 1:  # выбор четности
            parity = button
            weekday = second_row - 2
        else:  # выбор дня недели
            parity = first_row
            weekday = button - 2

        keyboard[0][parity][0] = '· {} ·'.format(keyboard[0][parity][0])
        keyboard[1][weekday][0] = '· {} ·'.format(keyboard[1][weekday][0])

        for row in keyboard:
            for button in row:
                button[1] = '{}_{}_{}'.format(button[1], parity, weekday+2)

        return cls.generate_inline_keyboard(keyboard)

    @classmethod
    def init_message(cls):
        message = """Я сообщение-расписание по дням. Жмякай на кнопки и получишь четкость и ясность"""
        """Учти, что при изменении в расписании сообщение само не обновится, поэтому при сомнениях - жмякай снова"""
        keyboard = deepcopy(cls.keyboard)
        for row in keyboard:
            for button in row:
                button[1] = '{}_{}_{}'.format(button[1], 0, 2)
        return message, cls.generate_inline_keyboard(keyboard)
