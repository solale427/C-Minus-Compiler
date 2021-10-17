import typing
from typing import List

from .errors import LexicalError
from ..token import Token, TokenType

if typing.TYPE_CHECKING:
    from .edge import Edge
    from ..scanner import Scanner


class NodeManager:
    nodes = {}

    @classmethod
    def add_node(cls, node):
        cls.nodes[node.id] = node

    @classmethod
    def get_node(cls, node_id):
        return cls.nodes[node_id]


class Node:
    nodes = {}

    def __init__(self, identifier, edges: List["Edge"] = [], is_end_node=False, has_lookahead=None):
        assert has_lookahead is None or is_end_node

        self.id = identifier
        self.edges_dict = {edge.character: edge for edge in edges}
        self.is_end_node = is_end_node
        self.has_lookahead = has_lookahead
        NodeManager.add_node(self)

    def add_edges(self, edges: ["Edge"]):
        for edge in edges:
            self.edges_dict[edge.character] = edge

    def move(self, character):
        if character in self.edges_dict:
            return self.edges_dict[character].destination
        else:
            return InvalidNode()

    def get_return_value(self, scanner: "Scanner"):
        assert self.is_end_node
        raise NotImplementedError


class FinalNUMNode(Node):

    def get_return_value(self, scanner: "Scanner"):
        return Token(token_type=TokenType.NUM, token_string=scanner.content[scanner.lexeme_beginning:scanner.forward])


class InvalidNumberNode(Node):
    def __init__(self):
        super().__init__(identifier=InvalidNumberNode, edges=[], is_end_node=True, has_lookahead=False)

    def get_return_value(self, scanner: "Scanner"):
        raise LexicalError('Invalid number')


class InvalidNode(Node):
    def __init__(self):
        super().__init__(identifier=InvalidNode, edges=[], is_end_node=True, has_lookahead=False)

    def move(self, character):
        return self

    def get_return_value(self, scanner: "Scanner"):
        raise LexicalError('Invalid input')
