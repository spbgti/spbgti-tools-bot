from telegrambot.states.validators.base import Validator
from telegrambot.states.validators.base import validation_message
from telegrambot.states.validators.base import ValidationResult

@validation_message('/start')
class StartCommandValidator(Validator):
    pass