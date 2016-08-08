from enum import Enum


class Validator:
    cancelWord = 'отмена'

    def validate(self, message):
        return self.validateCancel(message)

    def validateCancel(self, message):
        return (ValidationResult.Success, message) \
            if self.cancelWord not in message.lower() \
            else (ValidationResult.Cancel, message)


class SimpleMessageValidator(Validator):
    correct_message = ''

    def validate(self, message):
        baseValidation = super(Validator, self).validate(message)
        if baseValidation != ValidationResult.Success:
            return baseValidation
        return (ValidationResult.Success, message) \
            if message == self.correct_message \
            else (ValidationResult.Failure, message)

# TODO rename this, create simplevalidator for multimple messages
# TODO @multiple_validators([('student', Result.Student),('abitur', Result.Abitur), ('default', Result.None)])
def validation_message(msg):
    def real_decorator(cls):
        orig_init = cls.__init__

        def __init__(self, *args, **kws):
            self.correct_message = msg
            orig_init(self, *args, **kws)  # call the original __init__

        cls.__init__ = __init__  # set the class' __init__ to the new one
        return cls

    return real_decorator


class ValidationResult(Enum):
    Success = 1
    Failure = 2
    Cancel = 3
    Delete = 4
