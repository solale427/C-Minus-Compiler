from .symbol_table import SymbolTable


class Scanner:
    def __init__(self, content):
        self.content = content
        self.symbol_table = SymbolTable()
        self.current_line_number = None
        self.current_position = None

    def get_lexeme(self):
        pass

    def step_scan(self):
        pass

    def scan_through(self):
        self.current_line_number = 0
        self.current_position = 0
        while True:
            self.step_scan()
