from bot.states.base import State

from bot.states.validators.base import ValidationResult
from bot.states.validators.start_command import StartCommandValidator

output_message = 'Привет, это наш телеграм бот, и мы очень рады видеть тебя здесь!\n ' \
                 'По всем вопросам и предложениям пиши @b0g3r или @anamahpro (ну или @reflashwarlock),\n ' \
                 'они будут рады тебя выслушать.'

validator = StartCommandValidator()


def handle(message):
    res = validator.validate(message)
    if res == ValidationResult.Success:
        return State.WaitingStartState, ""
    return State.DisabledState, output_message
