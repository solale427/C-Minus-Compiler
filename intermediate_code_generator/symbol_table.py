import abc
from email import message
import typing
from collections import OrderedDict, defaultdict

from intermediate_code_generator.errors import NotDeclaredError, ParametersNumberMismatch, ParametersTypeMismatch, ValueTypeMismatchError

if typing.TYPE_CHECKING:
    from intermediate_code_generator.code_gen import ICG


class Value(abc.ABC):

    def __init__(self, value_type) -> None:
        super().__init__()
        self.type = value_type

    @abc.abstractmethod
    def get_value(self):
        pass


class ConstValue(Value):

    def __init__(self, value) -> None:
        super().__init__(value_type='int')
        self.value = value

    def get_value(self):
        return f'#{self.value}'


class IndirectValue(Value):
    def __init__(self, address) -> None:
        super().__init__(value_type='int')
        self.address = address

    def get_value(self):
        return f'@{self.address}'


class TemporaryValue(Value):

    def __init__(self, address) -> None:
        super().__init__(value_type='int')
        self.address = address

    def get_value(self):
        return self.address


class Symbol:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)


class VarSymbol(Symbol, Value):
    def __init__(self, name, value_type, size, memory_address, is_indirect=False) -> None:
        super().__init__(name, value_type=value_type)
        self.size = size
        self.memory_address = memory_address
        self.is_indirect = is_indirect

    def get_value(self):
        return self.memory_address


class FuncSymbol(Symbol):
    def __init__(self, name, jump_address, return_address_variable, return_type, return_variable) -> None:
        super().__init__(name)
        self.args_types = []
        self.arg_addresses = []
        self.jump_address = jump_address
        self.return_address_variable = return_address_variable
        self.return_type = return_type
        self.return_variable = return_variable

    @property
    def args_count(self):
        return len(self.args_types)

    def add_arg(self, var_name, var_type, var_size, icg: "ICG"):
        self.args_types.append(var_type)
        temp = icg.get_new_temporary_address()
        self.arg_addresses.append(temp)
        return temp

    def check_arg_types(self, icg, args):
        if len(self.args_types) != len(args):
            raise ParametersNumberMismatch(
                message=f'Mismatch in numbers of arguments of \'{self.name}\'.')
        for i, type in enumerate(self.args_types):
            if args[i].type != type:
                raise ParametersTypeMismatch(
                    message=f'Mismatch in type of argument {i+1} of \'{self.name}\'. Expected \'{type}\' but got \'{args[i].type}\' instead.')

    def call(self, icg: "ICG", args):
        for arg, arg_address in zip(args, self.arg_addresses):
            if arg.type == 'int' or arg.is_indirect:
                value = arg.get_value()
            else:
                value = ConstValue(arg.memory_address)
            icg.program_block.add_line(
                icg.program_block.assign,
                value,
                arg_address,
            )
        icg.program_block.add_line(
            icg.program_block.assign,
            f'#{icg.program_block.get_current_line() + 3}',
            self.return_address_variable,
        )
        icg.program_block.add_line(
            icg.program_block.jp,
            self.jump_address,
        )
        if self.return_type != 'void':
            temp = icg.get_new_temporary_address()
            icg.program_block.add_line(
                icg.program_block.assign,
                self.return_variable,
                temp,
            )
            return temp

    def do_return(self, icg: "ICG", return_value=None):
        if return_value is not None:
            icg.program_block.add_line(
                icg.program_block.assign,
                return_value,
                self.return_variable,
            )
        icg.program_block.add_line(
            icg.program_block.jp,
            f'@{self.return_address_variable.address}',
        )


class OutputFuncSymbol(FuncSymbol):
    def __init__(self):
        super().__init__(
            name='output',
            jump_address=-1,
            return_address_variable=None,
            return_type='void',
            return_variable=None,
        )
        self.args_types = ['int']

    def add_arg(self, var_name, var_type, var_size, icg: "ICG"):
        assert False

    def call(self, icg: "ICG", args):
        icg.program_block.add_line(
            icg.program_block.print, args[0].get_value())


class ICGSymbolTable:

    def __init__(self) -> None:
        self.table = defaultdict(dict)

    def insert_func(self, scope, func_symbol: FuncSymbol):
        self.table[scope][func_symbol.name] = func_symbol
        return func_symbol

    def insert_var(self, scope, var_symbol: VarSymbol):
        self.table.setdefault(scope, {})
        self.table[scope][var_symbol.name] = var_symbol

    def find_symbol(self, scope_stack: list, name):
        for scope in scope_stack[::-1]:
            if symbol := self.table[scope].get(name):
                return symbol

        raise NotDeclaredError(message=f'\'{name}\' is not defined.')


class Repeat:
    def __init__(self) -> None:
        self.breaks = []
