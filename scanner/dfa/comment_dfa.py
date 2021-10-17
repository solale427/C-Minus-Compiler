from scanner.dfa.edge import generate_edges, ALL_CHARACTERS
from scanner.dfa.errors import LexicalError
from scanner.dfa.node import Node
from scanner.scanner import Scanner
from scanner.token import Token, TokenType


class CommentFinalNode(Node):
    def get_return_value(self, scanner: "Scanner"):
        return Token(token_type=TokenType.COMMENT, token_string=scanner.get_lexeme())


class UnclosedCommentNode(Node):
    def __init__(self):
        super().__init__(identifier=UnclosedCommentNode, is_end_node=True, has_lookahead=False)

    def get_return_value(self, scanner: "Scanner"):
        raise LexicalError('Unclosed comment')


def comment_dfa():
    node_9 = Node(identifier=9)
    node_10 = Node(identifier=10)
    node_11 = Node(identifier=11)
    node_12 = Node(identifier=12)
    node_13 = CommentFinalNode(identifier=13, is_end_node=True)
    unclosed_comment = UnclosedCommentNode()
    node_9.edges_dict = generate_edges(destination=node_10, characters_to_include=['*']) + generate_edges(
        destination=node_12, characters_to_include=['/'])
    node_10.edges_dict = generate_edges(destination=node_10, characters_to_include=ALL_CHARACTERS,
                                        characters_to_exclude=['*']) + generate_edges(destination=node_11,
                                                                                      characters_to_include=['*'])
    node_11.edges_dict = generate_edges(destination=node_11, characters_to_include=['*']) + generate_edges(
        destination=node_13, characters_to_include=['/']) + generate_edges(destination=unclosed_comment,
                                                                           characters_to_include=[
                                                                               'eof']) + generate_edges(
        destination=node_10,
        characters_to_include=ALL_CHARACTERS,
        characters_to_exclude=[
            '*', '/', 'eof'])
    node_12.edges_dict = generate_edges(destination=node_13, characters_to_include=['\n', '']) + generate_edges(
        destination=node_12, characters_to_include=ALL_CHARACTERS, characters_to_exclude=['\n', ''])
