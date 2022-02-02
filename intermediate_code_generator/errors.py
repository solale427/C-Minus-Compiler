from email import message


class ICGError(Exception):
    def __init__(self, *args: object, message) -> None:
        super().__init__(*args)
        self.message = message


class InvalidBreakError(ICGError):
    pass


class ValueTypeMismatchError(ICGError):
    pass


class NotDeclaredError(ICGError):
    pass


class ParametersNumberMismatch(ICGError):
    pass


class ParametersTypeMismatch(ICGError):
    pass


class OperandsTypeMisMatch(ICGError):
    pass


class IllegalTypeError(ICGError):
    pass
