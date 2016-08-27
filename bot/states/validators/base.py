from enum import Enum


class Validator:
    cancelWord = 'отмена'

    def validate(self, message):
        return self.validateCancel(message)

    def validateCancel(self, message):
        return ValidationResult.Success \
            if self.cancelWord not in message.lower() \
            else ValidationResult.Cancel


class ValidationResult(Enum):
    Success = 1
    Failure = 2
    Cancel = 3
    Delete = 4
