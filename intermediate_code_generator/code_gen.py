from lib2to3.pgen2.grammar import opmap_raw
import opcode
from re import S
from this import s
from tkinter import N
from tkinter.messagebox import NO
from intermediate_code_generator.symbol_table import ICGSymboltTable, Repeat


class SemanticStack:

    def __init__(self) -> None:
        self._stack = []

    def push(self, input):
        self._stack.append(input)

    def pop(self):
        return self._stack.pop()


class InvalidBreakError(Exception):
    pass


class ValueTypeMismatchError(Exception):
    pass


class ICG:

    def __init__(self) -> None:
        self.scope_count = 0
        self.semantic_stack = SemanticStack()
        self.symbol_table = ICGSymboltTable()
        self.PB = []
        self.actions = {
            "ActionAddOp": self.add_op,
            "ActionMult": self.mult,
            "ActionPid": self.pid,
            "ActionAssign": self.assign,
            "ActionPushValue": self.push_value,
            "ActionNewScop": self.new_scope,
            "ActionEndScope": self.end_scope,
            "ActionJp": self.jp,
            "ActionJpfSave": self.jpf_save,
            "ActionLabel": self.label,
            "ActionUntil": self.until,
            "ActionRelOp": self.relop
        }
        self.scope_stack = []
        self.repeat_stack = []

    def perform_action(self, action_name, input):
        action = self.actions.get(action_name)
        action(input=input)

    def get_temp():
        pass

    def pid(self, input):
        symbol = self.symbol_table.find_adr(input)
        self.semantic_stack.append(symbol)

    def mult(self, input=None):
        temp = self.get_temp()
        operand1 = self.semantic_stack.pop()
        operand2 = self.semantic_stack.pop()
        self.PB.append(("MULT", operand1, operand2, temp))

    def add_op(self, input=None):
        temp = self.get_temp()
        operand1 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        operand2 = self.semantic_stack.pop()
        if op is "-":
            self.PB.append(("SUB", operand1, operand2, temp))
        else:
            self.PB.append(("ADD", operand1, operand2, temp))

    def assign(self, input=None):
        symbol = self.semantic_stack.pop()
        exp = self.semantic_stack.pop()
        if symbol.type != type(exp):
            raise ValueTypeMismatchError()
        self.PB.append(("ASSIGN", symbol, exp))

    def push_value(self, input):
        self.semantic_stack.push(input)

    def dec_var(self, input=None):
        size = self.semantic_stack.pop()
        var_type = self.semantic_stack.pop()
        var_name = self.semantic_stack.pop()
        self.symbol_table.insert_var(
            var_name=var_name,
            type=var_type,
            size=size,
            scope=self.scope_stack[-1]
        )

    def new_scope(self, input=None):
        self.scope_count += 1
        self.scope_stack.append(self.scope_count)

    def end_stack(self, input=None):
        self.scope_stack.pop()

    def jp(self, input=None):
        PBindex = self.semantic_stack.pop()
        self.PB[PBindex] = ("JP", len(self.PB))

    def jpf_save(self, input=None):
        PBindex = self.semantic_stack.pop()
        exp = self.semantic_stack.pop()
        self.PB[PBindex] = ("JPF", exp, len(self.PB)+1)
        self.semantic_stack.push(len(self.PB))

    def label(self, input=None):
        self.semantic_stack.push(len(self.PB))

    def until(self, input=None):
        exp = self.semantic_stack.pop()
        label = self.semantic_stack.pop()
        self.PB.append(("JPF", exp, label))
        self.semantic_stack.pop()
        repeat = self.repeat_stack.pop()
        for break_label in repeat.breaks:
            self.PB[break_label] = ("JP", len(self.PB))

    def repeat(self, input=None):
        self.repeat_stack.append(Repeat())

    def perform_break(self, input=None):
        if not self.repeat_stack:
            raise InvalidBreakError()
        repeat = self.repeat_stack[-1]
        repeat.breaks.append(len(self.PB))

    def relop(self, input=None):
        temp = self.get_temp()
        operand1 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        operand2 = self.semantic_stack.pop()
        if op == "<":
            temp = operand1 < operand2
        else:
            temp = operand1 == operand2
        self.semantic_stack.push(temp)
