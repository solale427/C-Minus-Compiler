import typing

from scanner.dfa.edge import generate_edges, ALL_CHARACTERS, EOF
from scanner.dfa.errors import LexicalError
from scanner.dfa.node import Node
from scanner.token import Token, TokenType

if typing.TYPE_CHECKING:
    from ..scanner import Scanner


class CommentFinalNode(Node):
    def get_return_value(self, scanner: "Scanner"):
        return Token(token_type=TokenType.COMMENT, token_string=self.get_lexeme_from_scanner(scanner))


class UnclosedCommentNode(Node):
    def __init__(self):
        super().__init__(identifier=UnclosedCommentNode, is_end_node=True, has_lookahead=False)

    def get_return_value(self, scanner: "Scanner"):
        # TODO: handle long unclosed comments
        return LexicalError(self.get_lexeme_from_scanner(scanner), 'Unclosed comment')


def comment_dfa():
    node_9 = Node(identifier=9)
    node_10 = Node(identifier=10)
    node_11 = Node(identifier=11)
    node_12 = Node(identifier=12)
    node_13 = CommentFinalNode(identifier=13, is_end_node=True)
    unclosed_comment = UnclosedCommentNode()
    node_9.edges = generate_edges(
        destination=node_10,
        characters_to_include=['*']
    ) + generate_edges(
        destination=node_12,
        characters_to_include=['/']
    )
    node_10.edges = generate_edges(
        destination=node_10,
        characters_to_include=ALL_CHARACTERS,
        characters_to_exclude=['*']
    ) + generate_edges(
        destination=node_11,
        characters_to_include=['*']
    ) + generate_edges(
        destination=unclosed_comment,
        characters_to_include=[EOF]
    )
    node_11.edges = generate_edges(
        destination=node_11,
        characters_to_include=['*']
    ) + generate_edges(
        destination=node_13,
        characters_to_include=['/']
    ) + generate_edges(
        destination=unclosed_comment,
        characters_to_include=[EOF]
    ) + generate_edges(
        destination=node_10,
        characters_to_include=ALL_CHARACTERS,
        characters_to_exclude=[
            '*',
            '/',
            EOF
        ]
    )
    node_12.edges = generate_edges(
        destination=node_13,
        characters_to_include=['\n', EOF]
    ) + generate_edges(
        destination=node_12,
        characters_to_include=ALL_CHARACTERS,
        characters_to_exclude=['\n', EOF]
    )

    return generate_edges(
        destination=node_9,
        characters_to_include=['/']
    )
