import typing

from scanner.dfa.edge import letters, digits, generate_edges, ALL_CHARACTERS, DIGIT_CHARACTERS, LETTER_CHARACTERS
from scanner.dfa.node import Node
from ..token import Token

if typing.TYPE_CHECKING:
    from ..scanner import Scanner


class FinalIdKeywordNode(Node):
    def get_return_value(self, scanner: "Scanner"):
        lexeme = self.get_lexeme_from_scanner(scanner)
        scanner.symbol_table.install(lexeme)
        return Token(token_type=scanner.symbol_table.get_type(lexeme), token_string=lexeme)


def id_keyword_dfa():
    node_3 = Node(identifier=3)
    node_4 = FinalIdKeywordNode(identifier=4, is_end_node=True, has_lookahead=True)
    node_3.edges = letters(destination=node_3) + digits(destination=node_3) + generate_edges(
        destination=node_4,
        characters_to_include=ALL_CHARACTERS,
        characters_to_exclude=DIGIT_CHARACTERS + LETTER_CHARACTERS)
    return letters(destination=node_3)
