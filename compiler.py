from parser.parser import Parser
from scanner.scanner import Scanner

if __name__ == '__main__':
    grammar_strings = []

    with open('input.txt') as f, \
            open('syntax_errors.txt', 'w') as errors_writer_file, \
            open('parse_tree.txt', 'w') as parse_tree_file:
        s = Scanner(content=f)
        s.setup_scan_through()
        p = Parser(s, errors_writer_file, parse_tree_file)

        with open('parser/grammar.txt') as grammar:
            p.create_diagram(grammar.readlines())
        v = p.parse()
