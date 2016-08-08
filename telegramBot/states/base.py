from telegrambot.helpers import Singleton


@Singleton
class State:
    OnSuccess = None
    OnFailure = None
    OnCancel = None
    OnDelete = None

    output = ''

    def answer(self):
        return self.output

    def handle(self, message):
        return message

    def needs_input(self):
        return True


class EpsilonState(State):
    def needs_input(self):
        return False


@Singleton
class StateAutomaton:
    InState = None
    OutState = None
    DeleteState = None
    CancelState = None
