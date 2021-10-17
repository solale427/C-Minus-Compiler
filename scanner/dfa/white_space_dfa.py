import typing

from scanner.dfa.edge import white_spaces
from scanner.dfa.node import Node
from scanner.token import Token, TokenType

if typing.TYPE_CHECKING:
    from ..scanner import Scanner


class WhiteSpaceFinalNode(Node):

    def get_return_value(self, scanner: "Scanner"):
        return Token(token_type=TokenType.WHITE_SPACE, token_string=self.get_lexeme_from_scanner(scanner))


def white_space_dfa():
    node_14 = WhiteSpaceFinalNode(identifier=14)
    return white_spaces(destination=node_14)
