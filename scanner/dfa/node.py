import typing

from .errors import LexicalError

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

    def __init__(self, identifier, is_end_node=False, has_lookahead=None):
        assert has_lookahead is None or is_end_node

        self.id = identifier
        self.is_end_node = is_end_node
        self._edges_dict = {}
        self.has_lookahead = has_lookahead
        NodeManager.add_node(self)

    @property
    def edges_dict(self):
        return self._edges_dict

    @edges_dict.setter
    def edges_dict(self, edges: ["Edge"]):
        self._edges_dict = {edge.character: edge for edge in edges}

    def move(self, character):
        if character in self.edges_dict:
            return self.edges_dict[character].destination
        else:
            return InvalidNode()

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
