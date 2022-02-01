from collections import OrderedDict
import re
from shutil import ExecError
from tkinter import S

from scanner.dfa.edge import symbols


class Symbol:
    def __init__(self) -> None:
        pass


class VarSymbol(Symbol):

    def __init__(self, var_type, scope, size, memory_address) -> None:
        super().__init__()
        self._scope = scope
        self._size = size
        self._type = var_type
        self._memory_address = memory_address

    @property
    def scope(self):
        return self._scope

    @property
    def size(self):
        return self._size

    @property
    def type(self):
        return self._type

    @property
    def memory_address(self):
        return self._memory_address


class FuncSymbol(Symbol):

    def __init__(self) -> None:
        super().__init__()


class NotDeclaredError(Exception):
    pass


class ICGSymboltTable:

    def __init__(self) -> None:
        self.free_memory_pointer = 0
        self.table = OrderedDict()

    def insert_var(self, scope, var_name, type, size):
        self.table.setdefault(scope, {})
        var_symbol = VarSymbol(
            scope=scope,
            memory_address=self.free_memory_pointer,
            var_type=type,
            size=size
        )
        self.table[scope][var_name] = var_symbol

    def find_symbol(self, scope_stack: list, var_name):
        for scope in scope_stack.reverse:
            if {symbol := self.table[scope].get(var_name)}:
                return symbol
        raise NotDeclaredError()


class Repeat:
    def __init__(self) -> None:
        self.breaks = []
