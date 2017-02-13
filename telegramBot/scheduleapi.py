import requests
from spbgtitoolsbot.settings import SCHEDULE_API
from datetime import date, timedelta


def get_schedule(group):
    return requests.get('{}/schedules/group/{}/year/{}/semester/{}'.format(
        SCHEDULE_API, group, 2016, 2)).json()['exercises']


def get_room(room_id):
    room = requests.get('{}/rooms/id/{}'.format(
        SCHEDULE_API, room_id)).json()
    return room['name']


def get_weekday_schedule(group, weekday, parity):
    schedule = get_schedule(group)
    return [exercise for exercise in schedule if
            exercise['day'] == str(weekday) and
            (exercise['parity'] is None or exercise['parity'] == str(parity))]


def get_date_schedule(group, day_date):
    _, week, weekday = day_date.isocalendar()
    if week % 2 == 0:
        parity = 1
    else:
        parity = 2
    return get_weekday_schedule(group, weekday, parity), weekday, parity


def get_today_schedule(group):
    return get_date_schedule(group, date.today())


def get_tomorrow_schedule(group):
    return get_date_schedule(group, date.today() + timedelta(days=1))
