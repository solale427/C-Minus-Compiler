from enum import Enum, auto


class TokenType(Enum):
    NUM = auto()
    SYMBOL = auto()
    KEYWORD = auto()
    ID = auto()


class Token:
    def __init__(self, token_type, token_string):
        self.token_type = token_type
        self.token_string = token_string
