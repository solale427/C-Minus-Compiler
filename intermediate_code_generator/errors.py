class ICGError(Exception):
    pass


class InvalidBreakError(ICGError):
    pass


class ValueTypeMismatchError(ICGError):
    pass


class NotDeclaredError(ICGError):
    pass
