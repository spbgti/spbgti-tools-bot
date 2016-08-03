from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from . import bot
from . import models
import os
import json


class BotTestCase(TestCase):

    def test_user_create(self):
        telegram_id = os.environ['TELEGRAM_ID']
        msg = {"message_id": 8,
               "from": {
                   "id": telegram_id,
                   "first_name": "Test-man",
                   "username": "Test-man"
               },
               "chat": {
                   "id": telegram_id,
                   "first_name": "Test-man",
                   "username": "Test-man",
                   "type": "private"
               },
               "date": 1470153003,
               "text": "test"
               }
        bot.handle(msg)
        test_man = models.User.objects.get(telegram_id=telegram_id)
        self.assertEqual(test_man.state, "RegistrationState")

