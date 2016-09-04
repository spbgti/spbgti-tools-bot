from bot.states.validators.base import ValidationResult
from bot.states.validators.base import Validator


class SimpleMessageValidator(Validator):
    validation_message = ''

    def validate(self, message):
        baseValidation = super(Validator, self).validate(message)
        if baseValidation != ValidationResult.Success:
            return baseValidation
        return ValidationResult.Success \
            if message == self.validation_message \
            else ValidationResult.Failure


# TODO rename this, create simplevalidator for multimple messages
# TODO @multiple_validators([('student', Result.Student),('abitur', Result.Abitur), ('default', Result.None)])
def validation_message(msg):
    def real_decorator(cls):
        orig_init = cls.__init__

        def __init__(self, *args, **kws):
            self.validation_message = msg
            orig_init(self, *args, **kws)  # call the original __init__

        cls.__init__ = __init__  # set the class' __init__ to the new one
        return cls

    return real_decorator
