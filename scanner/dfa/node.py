import abc
import typing

from .errors import LexicalError

if typing.TYPE_CHECKING:
    from .edge import Edge
    from ..scanner import Scanner
    from ..token import Token


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
            from .edge import C_MINUS_CHARACTERS
            return InvalidNode(has_lookahead=character in C_MINUS_CHARACTERS)

    def get_lexeme_from_scanner(self, scanner: "Scanner"):
        return scanner.get_lexeme(number_of_characters_to_remove_from_end=1 if self.has_lookahead is True else 0)

    @abc.abstractmethod
    def get_return_value(self, scanner: "Scanner") -> typing.Union["Token", "LexicalError"]:
        assert self.is_end_node
        raise NotImplementedError


class InvalidNode(Node):
    def __init__(self, has_lookahead=False):
        super().__init__(identifier=InvalidNode, is_end_node=True, has_lookahead=has_lookahead)

    def move(self, character):
        return self

    def get_return_value(self, scanner: "Scanner"):
        return LexicalError(self.get_lexeme_from_scanner(scanner), 'Invalid input')
