from anytree import RenderTree


class ErrorWriter:
    def __init__(self, file, parser):
        self.file = file
        self.parser = parser
        self.wrote = False

    def write_illegal(self):
        self.file.write(
            f'#{self.parser.scanner.lexeme_start_line + 1} : syntax error, illegal {self.parser.lookahead}\n')
        self.wrote = True

    def write_missing(self, missing_text):
        self.file.write(f'#{self.parser.scanner.lexeme_start_line + 1} : syntax error, missing {missing_text}\n')
        self.wrote = True

    def write_eof(self):
        self.file.write(f'#{self.parser.scanner.lexeme_start_line + 1} : syntax error, Unexpected EOF\n')
        self.wrote = True

    def done(self):
        if not self.wrote:
            self.file.write('There is no syntax error.\n')


class TreeWriter:
    def __init__(self, file, parser):
        self.file = file
        self.parser = parser

    def write_tree(self, root):
        for pre, fill, node in RenderTree(root):
            self.file.write("%s%s" % (pre, node.name) + '\n')
