from scanner.dfa.node import Node


class Edge:
    def __init__(self, destination, character):
        from .node import NodeManager
        self.destination = NodeManager.get_node(destination)
        self.character = character


def get_digit_character():
    return list(range(9))


def get_letter_characters():
    return list(map(chr, range(97, 123))) + list(map(chr, range(65, 91)))


def get_all_characters():
    return [chr(i) for i in range(32, 127)]


def generate_edges(destination, characters_to_include, characters_to_exclude=[]):
    return [Edge(destination, character) for character in characters_to_include
            if character not in characters_to_exclude]


def digits(destination: Node):
    return generate_edges(destination=destination, characters_to_include=range(9))


def letters(destination=None):
    return generate_edges(destination=destination,
                          characters_to_include=get_letter_characters())
