from .symbol_table import SymbolTable


def c_minus_dfa():
    pass


class Scanner:
    def __init__(self, content):
        self.content = content
        self.symbol_table = SymbolTable()
        self.current_line_number = None
        self.lexeme_beginning = None
        self.forward = None

    def get_lexeme(self):
        return self.content[self.lexeme_beginning:self.forward]

    def step_scan(self):
        pass

    def scan_through(self):
        self.current_line_number = 0
        self.lexeme_beginning = self.forward = 0

        while True:
            self.step_scan()
