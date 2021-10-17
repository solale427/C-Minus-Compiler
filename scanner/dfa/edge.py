from scanner.dfa.node import Node

ALL_CHARACTERS = [chr(i) for i in range(32, 127)]
DIGIT_CHARACTERS = list(range(10))
LETTER_CHARACTERS = list(map(chr, range(97, 123))) + list(map(chr, range(65, 91)))
SYMBOLS = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<']
WHITE_SPACES = [chr(32), chr(10), chr(13), chr(9), chr(11), chr(12)]
KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']


class Edge:
    def __init__(self, destination, character):
        from .node import NodeManager
        self.destination = NodeManager.get_node(destination)
        self.character = character


def generate_edges(destination, characters_to_include, characters_to_exclude=[]):
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
