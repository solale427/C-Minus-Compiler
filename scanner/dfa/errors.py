class LexicalError:
    def __init__(self, lexeme: str, error_message: str):
        self.lexeme = lexeme
        self.error_message = error_message

    def __str__(self):
        return self.error_message
