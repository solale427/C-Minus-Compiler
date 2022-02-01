from collections import defaultdict
from operator import le

from anytree import Node, RenderTree
from intermediate_code_generator.code_gen import ICG

from parser.writer import ErrorWriter, TreeWriter
from parser.transition_diagram.diagram import ActionState, NonTerminal, State, Edge, EMPTY_CHAIN, END_MARKER, Diagram
from scanner.dfa.edge import EOF
from scanner.token import TokenType


class DoneParsing(Exception):
    pass


class Parser:
    non_terminals = {}
    first_sets = {}
    follow_sets = {}
    predict_sets = []
    init_non_terminal = None

    def __init__(self, scanner, error_writer_file, tree_writer_file, icg):
        self.scanner = scanner
        self.error_writer = ErrorWriter(error_writer_file, self)
        self.tree_writer = TreeWriter(tree_writer_file, self)
        self.non_terminals = {}
        self.first_sets = {}
        self.follow_sets = defaultdict(set)
        self.predict_sets = []
        self.init_non_terminal = None
        self._token = None
        self.current_node = None
        self.icg = icg

    @staticmethod
    def check_token_is_terminal(token):
        return token[0] == '/' or token == EMPTY_CHAIN or token == END_MARKER

    @property
    def token(self):
        return self._token

    @property
    def lookahead(self):
        if self._token is None:
            return self.get_next_lookahead()
        if self._token is EOF:
            return END_MARKER
        if self._token.token_type in (TokenType.WHITE_SPACE, TokenType.COMMENT):
            return self.get_next_lookahead()
        if self._token.token_type not in [TokenType.ID, TokenType.NUM]:
            return self._token.token_string
        else:
            return self._token.token_type.name

    def get_next_lookahead(self):
        self._token = self.scanner.get_lookahead()
        return self.lookahead

    def get_rules(self, grammar_strings):
        rules = []
        nt = set()
        for grammar_string in grammar_strings:
            if not grammar_string.strip():
                continue
            start_state_name = grammar_string.split('->')[0].strip()
            nt.add(start_state_name)
            grammars = grammar_string.split('->')[1].strip().split('|')
            rules.extend([[start_state_name, g.strip().split()]
                         for g in grammars])
        return rules, nt

    def extend_grammar(self, rule, left):
        right = rule[1]
        if left.startswith("Action"):
            start_state = ActionState(is_final=False, action_name=left)
        else:
            start_state = State(is_final=False)
        node = start_state
        for i, g in enumerate(right):
            next_node = State(is_final=i == len(right) - 1)
            if not self.check_token_is_terminal(g):
                g = self.non_terminals[g]
            elif g not in [EMPTY_CHAIN, END_MARKER]:
                g = g[1:]
            node.add_edge(Edge(destination=next_node, token=g))
            node = next_node
        return start_state

    def create_diagram(self, grammar_strings):
        rules, nt = self.get_rules(grammar_strings)
        for i in nt:
            self.first_sets[i] = set()
            self.follow_sets[i] = set()
        self.make_first_sets(rules)
        self.make_follow_sets(rules)
        for i in nt:
            self.non_terminals[i] = NonTerminal(
                first=self.first_sets[i], follow=self.follow_sets[i], name=i)
        self.init_non_terminal = self.non_terminals[rules[0][0]]
        self.make_predict_sets(rules)
        for i, rule in enumerate(rules):
            left = rule[0]
            start = self.extend_grammar(rule, left)
            self.non_terminals[left].diagrams.append(
                Diagram(predict=self.predict_sets[i], first_state=start))

    def collect_set(self, initial_set, items, additional_set):
        s = set(initial_set)
        for i, item in enumerate(items):
            if not self.check_token_is_terminal(item):
                s = s.union(
                    set([it for it in self.first_sets[item] if it != EMPTY_CHAIN]))
                if EMPTY_CHAIN in self.first_sets[item]:
                    if i + 1 < len(items):
                        continue
                    s = s.union(additional_set)
                else:
                    return s
            else:
                s.add(item)
                return s
        return s

    def make_first_sets(self, rules):
        set_changed = True
        while set_changed:
            set_changed = False
            for rule in rules:
                left = rule[0]
                right = rule[1]
                s = self.first_sets[left]
                s = s.union(self.collect_set(s, right, [EMPTY_CHAIN]))
                if len(self.first_sets[left]) != len(s):
                    self.first_sets[left] = s
                    set_changed = True

    def make_follow_sets(self, rules):
        self.follow_sets[rules[0][0]].add(END_MARKER)
        set_changed = True
        while set_changed:
            set_changed = False
            for rule in rules:
                left = rule[0]
                right = rule[1]
                for i, item in enumerate(right):
                    s = self.follow_sets[item]
                    s = s.union(self.collect_set(s, right[i + 1:], self.follow_sets[left]) if i + 1 < len(right) else
                                self.follow_sets[left])
                    if len(self.follow_sets[item]) != len(s):
                        self.follow_sets[item] = s
                        set_changed = True

    def make_predict_sets(self, rules):
        for i, rule in enumerate(rules):
            left = rule[0]
            right = rule[1]
            first_item = right[0]
            s = set()
            if not self.check_token_is_terminal(first_item):
                s = s.union(self.collect_set(s, right, self.follow_sets[left]))
            if first_item == EMPTY_CHAIN:
                s = self.follow_sets[left]
            else:
                s.add(first_item)
            self.predict_sets.append(s)

    def go_up(self):
        self.current_node = self.current_node.parent

    def go_down_with_epsilon(self):
        self.go_down(Node(EMPTY_CHAIN.lower()))

    def go_down_with_lookahead(self):
        if self._token is EOF:
            text = '$'
        else:
            text = f'({self._token.token_type.name}, {self._token.token_string})'
        self.go_down(Node(text))

    def go_down_with_non_terminal(self, nt):
        self.go_down(Node(nt.name))

    def go_down(self, node):
        node.parent = self.current_node
        self.current_node = node

    def illegal_lookahead(self):
        if self._token is EOF:
            self.error_writer.write_eof()
            raise DoneParsing
        else:
            self.error_writer.write_illegal()
            self.get_next_lookahead()

    def write_missing(self, non_terminal):
        self.error_writer.write_missing(non_terminal.name)

    def write_missing_terminal(self, terminal):
        self.error_writer.write_missing(terminal)

    def delete_current_node(self):
        node = self.current_node
        self.go_up()
        node.parent = None

    def parse(self):
        root = Node('root')
        self.current_node = root
        try:
            self.init_non_terminal.find_diagram(self)
        except DoneParsing:
            self.delete_current_node()
        self.tree_writer.write_tree(root.children[0])
        self.error_writer.done()
