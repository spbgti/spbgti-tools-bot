from telegrambot.states.base import StateAutomaton
from telegrambot.states.base import State

from telegramBot.states.validators.base import ValidationResult
from telegramBot.states.validators.start_command import StartCommandValidator

from telegrambot.states.registration_state import RegistrationStateAutomaton


class DisabledStateAutomaton(StateAutomaton):
    class StartWaitingState(State):
        output_message = 'Привет, это наш телеграм бот, и мы очень рады видеть тебя здесь!\n ' \
                         'По всем вопросам и предложениям пиши @b0g3r или @anamahpro (ну или @reflashwarlock),\n ' \
                         'они будут рады тебя выслушать. \n' \
                         'А сейчас мы попросим тебя ответить на несколько вопросов:'

        OnSuccess = DisabledStateAutomaton.Instance().OutState

        def handle(self, message):
            res = StartCommandValidator().validate(message)
            if res == ValidationResult.Success:
                return (DisabledStateAutomaton.OutState, DisabledStateAutomaton.OutState.answer())
            return self.output_message

    InState = StartWaitingState.Instance()
    OutState = RegistrationStateAutomaton.RegistrationStartState.Instance()
