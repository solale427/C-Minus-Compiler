import typing

from .errors import LexicalError

if typing.TYPE_CHECKING:
    from .edge import Edge
    from ..scanner import Scanner


class Node:
    nodes = {}

    def __init__(self, identifier, is_end_node=False, has_lookahead=None):
        assert has_lookahead is None or is_end_node

        self.id = identifier
        self.is_end_node = is_end_node
        self._edges = {}
        self.has_lookahead = has_lookahead

    @property
    def edges(self):
        return self._edges

    @edges.setter
    def edges(self, edges: typing.List["Edge"]):
        self._edges = {edge.character: edge for edge in edges}

    def move(self, character):
        if character in self.edges:
            return self.edges[character].destination
        else:
            return InvalidNode()

    def get_lexeme_from_scanner(self, scanner: "Scanner"):
        pass

    def get_return_value(self, scanner: "Scanner"):
        assert self.is_end_node
        raise NotImplementedError


class InvalidNode(Node):
    def __init__(self):
        super().__init__(identifier=InvalidNode, is_end_node=True, has_lookahead=False)

    def move(self, character):
        return self

    def get_return_value(self, scanner: "Scanner"):
        raise LexicalError('Invalid input')
