import typing

from .token import Token, TokenType

if typing.TYPE_CHECKING:
    from .scanner import Scanner
    from .dfa.errors import LexicalError


class Writer:
    def __init__(self, opened_file: typing.TextIO):
        self.opened_file = opened_file

    def write_token(self, return_value: "Token", scanner: "Scanner"):
        if return_value.token_type in [TokenType.SYMBOL, TokenType.KEYWORD, TokenType.ID, TokenType.NUM]:
            if scanner.new_line:
                if not scanner.is_token_first_line:
                    self.opened_file.write('\n')
                self.opened_file.write(f'{scanner.current_line_number + 1}.\t')
                scanner.new_line = False
                scanner.is_token_first_line = False
            self.opened_file.write(f'({return_value.token_type.name}, {return_value.token_string}) ')

    def write_error(self, return_value: "LexicalError", scanner: "Scanner"):
        if scanner.lexeme_start_line != scanner.error_line:
            if scanner.error_line is not None:
                self.opened_file.write('\n')
            self.opened_file.write(
                f'{scanner.lexeme_start_line + 1}.\t({str(return_value.lexeme)}, {return_value.error_message}) ')
        else:
            self.opened_file.write(f'({str(return_value.lexeme)}, {return_value.error_message}) ')
        scanner.has_error = True
        scanner.error_line = scanner.lexeme_start_line

    def close_file(self):
        self.opened_file.close()
