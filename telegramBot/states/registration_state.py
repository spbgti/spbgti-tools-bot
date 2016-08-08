from telegrambot.states.base import StateAutomaton
from telegrambot.states.base import EpsilonState

class RegistrationStateAutomaton(StateAutomaton):
    class RegistrationStartState(EpsilonState):
        output_message = 'А сейчас мы попросим тебя ответить на несколько вопросов:'

