# -*- coding: utf-8 -*-

from django.db import models

from .states import states


class User(models.Model):
    times = (
                (1, '7:00'),
                (2, '7:30'),
                (3, '8:00')
            )
    telegram_id = models.CharField("Id аккаунта телеграм", max_length=12, unique=True, primary_key=True)
    state = models.CharField("Состояние", default="", max_length=150)
    is_student = models.BooleanField("Учащийся", blank=True, default=False)
    group_number = models.CharField("Номер группы", max_length=11, blank=True, null=True)
    notification_time = models.IntegerField("Уведомления", choices=times, blank=True, null=True)
    @classmethod
    def create(cls, telegram_id):
        user = cls(telegram_id=telegram_id)
        cls.change_state(user, states['Start'])
        return user

    def __str__(self):
        return self.telegram_id

    def get_state(self):
        return states[self.state]

    def change_state(self, state, silent=False):
        if state not in states.values():
            raise TypeError('Invalid state {}'.format(state))
        self.state = state.__name__
        self.save()
        if not silent:
            state.set(self)
