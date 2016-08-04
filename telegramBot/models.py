# -*- coding: utf-8 -*-

from django.db import models
from .states import *


class User(models.Model):
    telegram_id = models.CharField("Id аккаунта телеграм", max_length=12, unique=True, primary_key=True)
    state = models.CharField("Состояние", default="", max_length=150)
    is_student = models.BooleanField("Учащийся", blank=True, default=False)
    group_number = models.CharField("Номер группы", max_length=11, blank=True, null=True)

    @classmethod
    def create(cls, telegram_id):
        user = cls(telegram_id=telegram_id)
        cls.change_state(user, StartCommand())
        return user

    def __str__(self):
        return self.telegram_id

    def get_state(self):
        state = eval(self.state)()
        if isinstance(state, State):
            return state
        else:
            return None


    def change_state(self, state):
        if not isinstance(state, State):
            return None
        #TODO: костыль с chat-id, используется from-id
        state.start(self.telegram_id, self)
        self.state = state.__class__.__name__
        self.save()