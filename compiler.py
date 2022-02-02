from intermediate_code_generator.code_gen import ICG
from parser.parser import Parser
from scanner.scanner import Scanner

if __name__ == '__main__':
    grammar_strings = []

    with open('input.txt') as f, \
            open('syntax_errors.txt', 'w') as errors_writer_file, \
            open('parse_tree.txt', 'w') as parse_tree_file:
        s = Scanner(content=f)
        s.setup_scan_through()
        icg = ICG(s)
        icg.setup()
        p = Parser(s, errors_writer_file, parse_tree_file, icg)

        with open('parser/grammar.txt') as grammar:
            p.create_diagram(grammar.readlines())
        v = p.parse()
        with open('output.txt', 'w') as out:
            icg.program_block.print_all(out, icg.has_semantic_error, icg.error_file)
