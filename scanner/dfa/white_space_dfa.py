from scanner.dfa.node import Node
from scanner.token import Token, TokenType
from scanner.scanner import Scanner


class WhiteSpaceFinalNode(Node):

    def get_return_value(self, scanner: "Scanner"):
        return Token(token_type=TokenType.WHITE_SPACE, token_string=scanner.get_lexeme())


def white_space_dfa():
    node_14 = WhiteSpaceFinalNode(identifier=14)
