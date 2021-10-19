from enum import Enum, auto


class TokenType(Enum):
    NUM = auto()
    ID = auto()
    KEYWORD = auto()
    SYMBOL = auto()
    COMMENT = auto()
    WHITE_SPACE = auto()


class Token:
    def __init__(self, token_type: TokenType, token_string: str):
        self.token_type = token_type
        self.token_string = token_string
