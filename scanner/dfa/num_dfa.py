from .edge import generate_edges, digits, letters, ALL_CHARACTERS, LETTER_CHARACTERS, DIGIT_CHARACTERS
from .errors import LexicalError
from .node import Node
from ..scanner import Scanner
from ..token import Token, TokenType


class FinalNUMNode(Node):

    def get_return_value(self, scanner: "Scanner"):
        return Token(token_type=TokenType.NUM, token_string=scanner.get_lexeme())


class InvalidNumberNode(Node):
    def __init__(self):
        super().__init__(identifier=InvalidNumberNode, is_end_node=True, has_lookahead=False)

    def get_return_value(self, scanner: "Scanner"):
        raise LexicalError('Invalid number')


def num_dfa():
    node_1 = Node(identifier=2)
    node_2 = FinalNUMNode(identifier=2, is_end_node=True)
    invalid_number = InvalidNumberNode()
    node_1.set_edges_dict = digits(destination=node_1) + \
                            letters(invalid_number) + \
                            generate_edges(destination=node_2,
                                           characters_to_include=ALL_CHARACTERS,
                                           characters_to_exclude=DIGIT_CHARACTERS + LETTER_CHARACTERS)
