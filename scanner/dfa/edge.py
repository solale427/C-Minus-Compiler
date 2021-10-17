class Edge:
    def __init__(self, destination, character):
        from .node import NodeManager
        self.destination = NodeManager.get_node(destination)
        self.character = character


def generate_edges(destination, characters_to_include, characters_to_exclude):
    return [Edge(destination, character) for character in characters_to_include
            if character not in characters_to_exclude]
