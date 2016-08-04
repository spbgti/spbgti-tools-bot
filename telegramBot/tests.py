from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from . import bot
from . import models
from . import states
import os
import json
from mock import patch, Mock




class BotTestCase(TestCase):
    telegram_id = os.environ['TELEGRAM_ID']
    msg = {"message_id": 8, "from": {"id": telegram_id, "first_name": "Test-man", "username": "Test-man"},
           "chat": {"id": telegram_id, "first_name": "Test-man", "username": "Test-man", "type": "private"},
           "date": 1470153003, "text": "test"}

    def test_user_create(self):
        states.State.send_message = Mock(side_effect=(lambda *args, **kwargs: print(args)))
        bot.handle(self.msg)
        #: None -> `CommandStart` -> `Registration`
        test_man = models.User.objects.get(telegram_id=self.telegram_id)
        self.assertEqual(test_man.state, "Registration")

    '''
    def test_registration_as_enrollee(self):
        #: `Registration` -> `RegistrationSuccess`
        test_man = models.User.objects.get(telegram_id=self.telegram_id)
        self.msg['text'] = test_man.get_state().possible_response[0]
        bot.handle(self.msg)
        test_man = models.User.objects.get(telegram_id=self.telegram_id)
        self.assertEqual(test_man.state, "RegistrationSuccess")
    '''