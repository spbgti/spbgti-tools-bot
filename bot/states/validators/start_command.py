from bot.states.validators.simple_validator import SimpleMessageValidator
from bot.states.validators.simple_validator import validation_message


@validation_message('/start')
class StartCommandValidator(SimpleMessageValidator):
    pass
