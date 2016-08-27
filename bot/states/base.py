from enum import Enum


class State(Enum):
    DisabledState = 0
    WaitingPersonTypeState = 1


class StateFactory:
    @staticmethod
    def getState(state):
        if state == State.DisabledState:
            from bot.states.disabled_state import handle
            return handle
        elif state == State.WaitingPersonTypeState:
            from bot.states.registration_state import handle
            return handle
        else:
            raise NotImplementedError
