from collections import OrderedDict

from .token import TokenType


class SymbolTable:
    def __init__(self):
        self.d = OrderedDict()

    def add_keyword(self, keyword):
        self.d[keyword] = TokenType.KEYWORD

    def install(self, entry):
        self.d.setdefault(entry, TokenType.ID)

    def get_type(self, entry):
        return self.d[entry]
