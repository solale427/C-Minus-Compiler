from .dfa.comment_dfa import comment_dfa
from .dfa.id_keyword_dfa import id_keyword_dfa
from .dfa.node import Node
from .dfa.num_dfa import num_dfa
from .dfa.symbol_dfa import symbol_dfa
from .dfa.white_space_dfa import white_space_dfa
from .symbol_table import SymbolTable


def c_minus_dfa():
    initial_node = Node(identifier=0)
    initial_node.edges = num_dfa() + id_keyword_dfa() + symbol_dfa() + comment_dfa() + white_space_dfa()


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
