import typing

from scanner.dfa.edge import generate_edges, ALL_CHARACTERS, SYMBOLS
from scanner.dfa.errors import LexicalError
from scanner.dfa.node import Node
from scanner.token import Token, TokenType

if typing.TYPE_CHECKING:
    from ..scanner import Scanner


class SymbolFinalNode(Node):
    def get_return_value(self, scanner: "Scanner"):
        return Token(token_type=TokenType.SYMBOL, token_string=self.get_lexeme_from_scanner(scanner))


class UnmatchedCommentNode(Node):
    def __init__(self):
        super().__init__(identifier=UnmatchedCommentNode, is_end_node=True, has_lookahead=False)

    def get_return_value(self, scanner: "Scanner"):
        return LexicalError(self.get_lexeme_from_scanner(scanner), 'Unmatched comment')


def symbol_dfa():
    node_5 = SymbolFinalNode(identifier=5, is_end_node=True)
    node_6 = Node(identifier=6)
    node_7 = SymbolFinalNode(identifier=7, is_end_node=True)
    node_8 = SymbolFinalNode(identifier=8, is_end_node=True, has_lookahead=True)
    node_15 = Node(identifier=15)
    node_16 = SymbolFinalNode(identifier=15, is_end_node=True)
    unmatched_comment = UnmatchedCommentNode()
    node_6.edges = generate_edges(
        destination=node_7,
        characters_to_include=['=']
    ) + generate_edges(
        destination=node_8,
        characters_to_include=ALL_CHARACTERS,
        characters_to_exclude=['=']
    )
    node_15.edges = generate_edges(
        destination=node_16,
        characters_to_include=ALL_CHARACTERS,
        characters_to_exclude=['/']
    ) + generate_edges(
        destination=unmatched_comment,
        characters_to_include=['/']
    )

    return generate_edges(
        destination=node_5,
        characters_to_include=SYMBOLS,
        characters_to_exclude=['=', '*']
    ) + generate_edges(
        destination=node_6,
        characters_to_include=['=']
    ) + generate_edges(
        destination=node_15,
        characters_to_include=['*']
    )
