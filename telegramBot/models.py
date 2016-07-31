from django.db import models


class User(models.Model):
    telegram_id = models.CharField("Id аккаунта телеграм", max_length=12, unique=True, primary_key=True)
    state = models.CharField("Состояние", default="start", max_length=100)
    group_number = models.CharField("Номер группы", max_length=11, blank=True, null=True)

    def __str__(self):
        return self.telegram_id

