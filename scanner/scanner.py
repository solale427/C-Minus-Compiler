from .dfa.edge import Edge, generate_edges, digits, letters, get_all_characters, get_letter_characters, \
    get_digit_character
from .dfa.node import Node, FinalNUMNode, InvalidNumberNode
from .symbol_table import SymbolTable


def num_dfa(initial_node: Node):
    node_1 = Node(identifier=2)
    node_1.add_edges(digits(destination=node_1))
    initial_node.add_edges(digits(destination=node_1))
    node_2 = FinalNUMNode(identifier=2, is_end_node=True)
    invalid_number = InvalidNumberNode()
    node_1.add_edges(letters(invalid_number))
    node_1.add_edges(
        generate_edges(destination=node_2, characters_to_include=get_all_characters(),
                       characters_to_exclude=get_digit_character() + get_letter_characters()))


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
        pass

    def step_scan(self):
        pass

    def scan_through(self):
        self.current_line_number = 0
        self.lexeme_beginning = self.forward = 0

        while True:
            self.step_scan()
