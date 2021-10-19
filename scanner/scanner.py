import typing
from typing import Optional, TextIO

from .dfa.comment_dfa import comment_dfa
from .dfa.edge import EOF
from .dfa.errors import LexicalError
from .dfa.id_keyword_dfa import id_keyword_dfa
from .dfa.node import Node
from .dfa.num_dfa import num_dfa
from .dfa.symbol_dfa import symbol_dfa
from .dfa.white_space_dfa import white_space_dfa
from .symbol_table import SymbolTable
from .token import Token, TokenType


def c_minus_dfa() -> Node:
    initial_node = Node(identifier=0)
    initial_node.edges = num_dfa() + id_keyword_dfa() + symbol_dfa() + comment_dfa() + white_space_dfa()
    return initial_node


class DoneScanning(Exception):
    pass


class Scanner:
    def __init__(self, content: TextIO):
        self.content = content
        self.symbol_table = SymbolTable()
        self.initial_node = c_minus_dfa()
        self.current_node: Optional[Node] = None
        self.so_far_lexeme = None
        self.last_char = None
        self.should_go_back = False

        self.current_line_number = None

    def get_lexeme(self, number_of_characters_to_remove_from_end=0):
        if not number_of_characters_to_remove_from_end:
            return self.so_far_lexeme
        else:
            return self.so_far_lexeme[:-number_of_characters_to_remove_from_end]

    def move_to_next_character(self) -> str:
        """
            Moves to the next character and adds it to so_far_lexeme
        :return: return the current character
        """

        if not self.should_go_back:
            if self.last_char == '\n':
                self.current_line_number += 1
                print()
            self.last_char = self.content.read(1)
        self.should_go_back = False
        self.so_far_lexeme += self.last_char
        return self.last_char

    def go_one_character_back(self):
        self.should_go_back = True

    def handle_return_value(self, return_value: typing.Union[Token, LexicalError]):
        if isinstance(return_value, Token):
            if return_value.token_type != TokenType.WHITE_SPACE:
                print((str(return_value.token_type), return_value.token_string), end=' ')
        else:
            print('***********ERROR:', (str(return_value.lexeme), return_value.error_message), end=' ')

    def handle_end_node(self):
        return_value = self.current_node.get_return_value(self)
        self.handle_return_value(return_value)
        if self.current_node.has_lookahead:
            self.go_one_character_back()

    def setup_step_scan(self):
        self.so_far_lexeme = ''
        self.current_node = self.initial_node

    def step_scan(self):
        self.setup_step_scan()
        current_char = ''
        while not self.current_node.is_end_node:
            current_char = self.move_to_next_character()
            if current_char == '':
                current_char = EOF
            self.current_node = self.current_node.move(current_char)

        self.handle_end_node()
        if current_char == EOF:
            raise DoneScanning

    def setup_scan_through(self):
        self.current_line_number = 0

    def scan_through(self):
        self.setup_scan_through()
        while True:
            try:
                self.step_scan()
            except DoneScanning:
                break
