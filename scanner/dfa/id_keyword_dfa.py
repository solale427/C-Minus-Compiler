from scanner.dfa.edge import letters, digits, generate_edges, ALL_CHARACTERS, DIGIT_CHARACTERS, LETTER_CHARACTERS, \
    KEYWORDS
from scanner.dfa.node import Node
from scanner.symbol_table import SymbolTable


class FinalIdKeywordNode(Node):
    pass


def id_keyword_dfa():
    symbol_table = SymbolTable()
    for keyword in KEYWORDS:
        symbol_table.add_keyword(keyword)
    node_3 = Node(identifier=3)
    node_4 = FinalIdKeywordNode(identifier=4, is_end_node=True)
    node_3.edges = letters(destination=node_3) + digits(destination=node_3) + generate_edges(
        destination=node_4,
        characters_to_include=ALL_CHARACTERS,
        characters_to_exclude=DIGIT_CHARACTERS + LETTER_CHARACTERS)
    return letters(destination=node_3)
