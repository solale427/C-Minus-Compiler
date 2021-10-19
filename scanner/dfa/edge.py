import string

from scanner.dfa.node import Node

ALL_CHARACTERS = [chr(i) for i in range(0, 127)]
DIGIT_CHARACTERS = string.digits
LETTER_CHARACTERS = string.ascii_letters
SYMBOLS = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<']
WHITE_SPACES = string.whitespace
KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']


class EOF:
    pass


class Edge:
    def __init__(self, destination: Node, character):
        self.destination = destination
        self.character = character


def generate_edges(destination: Node, characters_to_include, characters_to_exclude=[]):
    return [Edge(destination, character) for character in characters_to_include
            if character not in characters_to_exclude]


def digits(destination: Node):
    return generate_edges(destination=destination, characters_to_include=DIGIT_CHARACTERS)


def symbols(destination: Node):
    return generate_edges(destination=destination, characters_to_include=SYMBOLS)


def letters(destination: Node):
    return generate_edges(destination=destination,
                          characters_to_include=LETTER_CHARACTERS)


def white_spaces(destination: Node):
    return generate_edges(destination=destination,
                          characters_to_include=WHITE_SPACES)
