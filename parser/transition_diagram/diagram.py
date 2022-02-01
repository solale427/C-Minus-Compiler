from scanner.scanner import DoneScanning

EMPTY_CHAIN = 'EPSILON'
END_MARKER = '$'


class Diagram:
    def __init__(self, predict, first_state):
        self.first_state = first_state
        self.predict = predict


class NonTerminal:

    def __init__(self, first, follow, name):
        self.name = name
        self.first = first
        self.follow = follow
        self.diagrams = []

    def normalized_lookahead(self, lookahead):
        if lookahead in [EMPTY_CHAIN, END_MARKER]:
            return lookahead
        else:
            return '/' + lookahead

    def find_diagram(self, parser, go_down=True):
        try:
            if go_down:
                parser.go_down_with_non_terminal(self)
            for d in self.diagrams:
                if self.normalized_lookahead(parser.lookahead) in d.predict:
                    d.first_state.procedure(parser)
                    parser.go_up()
                    return
            if self.normalized_lookahead(parser.lookahead) in self.follow:
                parser.write_missing(self)
                parser.delete_current_node()
                return
            else:
                parser.illegal_lookahead()
                self.find_diagram(parser, go_down=False)
                return
        except DoneScanning:
            parser.delete_current_node()
            raise


class State:

    def __init__(self, is_final):
        self.is_final = is_final
        self.edge = None

    def add_edge(self, edge):
        self.edge = edge

    def procedure(self, parser):
        if self.is_final:
            return
        if self.edge.token_is_terminal:
            if self.edge.token == EMPTY_CHAIN:
                parser.go_down_with_epsilon()
                parser.go_up()
                self.edge.destination.procedure(parser)
                return
            elif parser.lookahead == self.edge.token:
                parser.go_down_with_lookahead()
                parser.go_up()
                parser.get_next_lookahead()
                self.edge.destination.procedure(parser)
                return
            else:
                parser.write_missing_terminal(self.edge.token)
                self.edge.destination.procedure(parser)
                return

        self.edge.token.find_diagram(parser)
        self.edge.destination.procedure(parser)
        return


class ActionState(State):

    def __init__(self, is_final, action_name):
        super().__init__(is_final)
        self.action_name = action_name

    def procedure(self, parser):
        parser.ICG.perform_action(self.action_name, parser.lookahead)


class Edge:
    def __init__(self, destination: State, token):
        self.destination = destination
        self.token = token

    @property
    def token_is_terminal(self):
        return isinstance(self.token, str)
