from typing import List

from .errors import ICGError, ValueTypeMismatchError, InvalidBreakError, OperandsTypeMisMatch, IllegalTypeError
from .symbol_table import (
    ICGSymbolTable,
    Repeat,
    FuncSymbol,
    OutputFuncSymbol,
    VarSymbol,
    ConstValue,
    TemporaryValue,
    Value, IndirectValue,
)


class SemanticStack:

    def __init__(self) -> None:
        self._stack = []

    def push(self, inp):
        self._stack.append(inp)

    def pop(self):
        return self._stack.pop()

    def last(self):
        return self._stack[-1]

    def first(self):
        return self._stack[0] if len(self._stack) else None


class ProgramBlock:
    add = 'ADD'
    mult = 'MULT'
    sub = 'SUB'
    eq = 'EQ'
    lt = 'LT'
    assign = 'ASSIGN'
    jpf = 'JPF'
    jp = 'JP'
    print = 'PRINT'

    def __init__(self):
        self.program = []

    def add_empty_line(self):
        self.program.append(None)

    def add_line(self, opcode, *operands):
        self.add_empty_line()
        self.change_line(len(self.program) - 1, opcode, *operands)

    def change_line(self, line, opcode, *operands):
        self.program[line] = [opcode, *operands]

    def get_current_line(self):
        return len(self.program) - 1

    def print_all(self, f, has_error, error_f):
        if has_error:
            print('The code has not been generated.', file=f)
        else:
            print('The input program is semantically correct.', file=error_f)
            for i, line in enumerate(self.program):
                x = [' ', ' ', ' ', ' ']
                for j, operand in enumerate(line):
                    if isinstance(operand, Value):
                        operand = operand.get_value()
                    x[j] = str(operand)
                x[0] = '(' + x[0]
                x[-1] += ' )'
                print(i, '\t', end='', sep='', file=f)
                print(*x, sep=', ', file=f)


class RunTimeMemory:

    def __init__(self, program_block: ProgramBlock) -> None:
        self.program_block = program_block
        self.top = IndirectValue(
            address=0
        )

    def push_func_vars(self, func, caller, temp_vars):
        if type(func) != OutputFuncSymbol and func.name == caller.name:
            self._push_func_vars(func=func, temp_vars=temp_vars)

    def pop_func_vars(self, function, caller, temp_vars):
        if type(function) != OutputFuncSymbol and function.name == caller.name:
            self._pop_func_vars(function, temp_vars)

    def _push_func_vars(self, func: FuncSymbol, temp_vars):
        self.program_block.add_line(
            self.program_block.assign, func.return_address_variable, self.top
        )
        self.program_block.add_line(
            self.program_block.add, ConstValue(
                4), TemporaryValue(0), TemporaryValue(0)
        )
        for var in func.variables[::-1] + temp_vars:
            # self.program_block.add_line(
            #     self.program_block.print, TemporaryValue(0))
            if isinstance(var, IndirectValue):
                var = TemporaryValue(var.address)
            self.program_block.add_line(
                self.program_block.assign, var, self.top
            )
            self.program_block.add_line(
                self.program_block.add, ConstValue(
                    4), TemporaryValue(0), TemporaryValue(0)
            )

    def _pop_func_vars(self, func: FuncSymbol, temp_vars):
        for var in temp_vars[::-1] + func.variables:
            if isinstance(var, IndirectValue):
                var = TemporaryValue(var.address)
            # self.program_block.add_line(
            #     self.program_block.print, TemporaryValue(0))
            self.program_block.add_line(
                self.program_block.sub,
                TemporaryValue(0), ConstValue(
                    4), TemporaryValue(0)
            )
            self.program_block.add_line(
                self.program_block.assign, self.top, var)
        self.program_block.add_line(
            self.program_block.sub,
            TemporaryValue(0), ConstValue(
                4), TemporaryValue(0)
        )
        self.program_block.add_line(
            self.program_block.assign, self.top, func.return_address_variable)


class ICG:

    def __init__(self, s) -> None:
        self.errors_file_path = 'semantic_errors.txt'
        self.scope_count = 0
        self.semantic_stack = SemanticStack()
        self.symbol_table = ICGSymbolTable()
        self.program_block = ProgramBlock()
        self.actions = {
            'ActionAddOp': self.add_op,
            'ActionMult': self.mult,
            'ActionPid': self.pid,
            'ActionAssign': self.assign,
            'ActionPushValue': self.push_value,
            'ActionNewScope': self.new_scope,
            'ActionEndScope': self.end_scope,
            'ActionJp': self.jp,
            'ActionJpfSave': self.jpf_save,
            'ActionLabel': self.label,
            'ActionUntil': self.until,
            'ActionRelOp': self.relop,
            'ActionBreak': self.perform_break,
            'ActionDecVar': self.dec_var,
            'ActionPushSize': self.push_size,
            'ActionPushNum': self.push_num,
            'ActionCallFunction': self.call_function,
            'ActionPop': self.pop,
            'ActionDecFunc': self.dec_func,
            'ActionDecFuncVar': self.dec_func_var,
            'ActionReturn': self.action_return,
            'ActionRepeat': self.repeat,
            'ActionJpf': self.jpf,
            'ActionNoAssignReturn': self.action_no_assign_return,
            'ActionGetIndex': self.get_index,
            'ActionPushSizePrime': self.push_size_prime,
            'ActionPopFunction': self.pop_function,
        }
        self.scope_stack = []
        self.repeat_stack: List[Repeat] = []
        self.variables_memory_pointer = 100
        self.temporary_memory_pointer = 500
        self.error_file = open(self.errors_file_path, 'w')
        self.s = s
        self.has_semantic_error = False
        self.run_time_memory = RunTimeMemory(program_block=self.program_block)

    def setup(self):
        self.program_block.add_line(
            self.program_block.assign, ConstValue(4), TemporaryValue(0))
        self.program_block.add_empty_line()
        self.symbol_table.insert_func(
            scope=0,
            func_symbol=OutputFuncSymbol(),
        )

    def get_new_variable_address(self, size=1):
        variable_address = self.temporary_memory_pointer
        if isinstance(size, ConstValue):
            size = size.value
        self.temporary_memory_pointer += 4 * int(size)
        return variable_address

    def get_new_temporary_address(self, size=1):
        temporary_address = self.get_new_variable_address(size)
        value = TemporaryValue(
            address=temporary_address,
        )
        return value

    def get_inp_from_token(self, token):
        return getattr(token, 'token_string', None)

    def perform_action(self, action_name, token):
        try:
            action = self.actions[action_name]
            action(self.get_inp_from_token(token))
            pass
        except ICGError as e:
            self.has_semantic_error = True
            self.error_file.write(
                f"#{self.s.current_line_number+1} : Semantic Error! " + e.message+"\n")
            if e.__class__ != IllegalTypeError:
                temp = self.get_new_temporary_address()
                self.semantic_stack.push(temp)
                # if self.scope_func:
                #     self.scope_func.push_variable(temp)

    def check_operand_types(self, op1, op2, expected):
        if op1.type != expected:
            raise OperandsTypeMisMatch(
                message=f'Type mismatch in operands, Got {op1.type} instead of {expected}.')
        if op2.type != expected:
            raise OperandsTypeMisMatch(
                message=f'Type mismatch in operands, Got {op2.type} instead of {expected}.')

    def pid(self, inp):
        symbol = self.symbol_table.find_symbol(self.scope_stack, inp)
        self.semantic_stack.push(symbol)

    def mult(self, inp):
        temp = self.get_new_temporary_address()
        # if self.scope_func:
        #     self.scope_func.push_variable(temp)
        operand1 = self.semantic_stack.pop()
        operand2 = self.semantic_stack.pop()
        self.check_operand_types(operand1, operand2, 'int')
        self.program_block.add_line(
            self.program_block.mult, operand1, operand2, temp)
        self.semantic_stack.push(temp)

    def add_op(self, inp):
        temp = self.get_new_temporary_address()
        # if self.scope_func:
        #     self.scope_func.push_variable(temp)
        operand2 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        operand1 = self.semantic_stack.pop()
        self.check_operand_types(operand1, operand2, 'int')
        if op == '-':
            opcode = self.program_block.sub
        else:
            opcode = self.program_block.add
        self.program_block.add_line(opcode, operand1, operand2, temp)
        self.semantic_stack.push(temp)

    def assign(self, inp):
        symbol = self.semantic_stack.pop()
        exp = self.semantic_stack.pop()
        self.check_operand_types(exp, symbol, symbol.type)
        self.program_block.add_line(self.program_block.assign, symbol, exp)
        self.semantic_stack.push(exp)

    def push_value(self, inp):
        self.semantic_stack.push(inp)

    def get_var_from_stack(self):
        var_name = self.semantic_stack.pop()
        var_type = self.semantic_stack.pop()
        if var_type == 'void':
            raise IllegalTypeError(
                message=f"Illegal type of void for '{var_name}'.")
        if var_type == 'array':
            var_size = self.semantic_stack.pop()
        else:
            var_size = 1
        return var_name, var_type, var_size

    def dec_var(self, inp):
        var_name, var_type, var_size = self.get_var_from_stack()
        var_symbol = VarSymbol(
            name=var_name,
            value_type=var_type,
            size=var_size,
            memory_address=self.get_new_variable_address(var_size),
        )
        self.symbol_table.insert_var(
            scope=self.scope_stack[-1],
            var_symbol=var_symbol,
        )
        self.program_block.add_line(
            self.program_block.assign, ConstValue(0), var_symbol)
        if isinstance(self.semantic_stack.first(), FuncSymbol):
            self.semantic_stack.first().push_variable(var_symbol)

    def new_scope(self, inp):
        self.scope_stack.append(self.scope_count)
        self.scope_count += 1

    def end_scope(self, inp):
        self.scope_stack.pop()

    def jp(self, inp):
        index = self.semantic_stack.pop()
        self.program_block.change_line(
            index, self.program_block.jp, self.program_block.get_current_line() + 1)

    def jpf(self, inp):
        index = self.semantic_stack.pop()
        exp = self.semantic_stack.pop()
        self.program_block.change_line(
            index, self.program_block.jpf, exp, self.program_block.get_current_line() + 1)

    def jpf_save(self, inp):
        index = self.semantic_stack.pop()
        exp = self.semantic_stack.pop()

        self.program_block.add_empty_line()
        self.semantic_stack.push(self.program_block.get_current_line())

        self.program_block.change_line(
            index, self.program_block.jpf, exp, self.program_block.get_current_line() + 1)

    def label(self, inp):
        self.program_block.add_empty_line()
        self.semantic_stack.push(self.program_block.get_current_line())

    def until(self, inp):
        exp = self.semantic_stack.pop()
        index = self.semantic_stack.pop()
        self.program_block.add_line(self.program_block.jpf, exp, index)
        repeat = self.repeat_stack.pop()
        for break_label in repeat.breaks:
            self.program_block.change_line(
                break_label,
                self.program_block.jp,
                self.program_block.get_current_line() + 1
            )

    def repeat(self, inp):
        self.repeat_stack.append(Repeat())
        self.semantic_stack.push(self.program_block.get_current_line() + 1)

    def perform_break(self, inp):
        if not self.repeat_stack:
            raise InvalidBreakError(
                message='No \'repeat ... until\' found for \'break\'.')
        repeat = self.repeat_stack[-1]
        self.program_block.add_empty_line()
        repeat.breaks.append(self.program_block.get_current_line())
        self.semantic_stack.push('chert')

    def relop(self, inp):
        temp = self.get_new_temporary_address()
        # if self.scope_func:
        #     self.scope_func.push_variable(temp)
        operand2 = self.semantic_stack.pop()
        op = self.semantic_stack.pop()
        operand1 = self.semantic_stack.pop()
        self.check_operand_types(op1=operand1, op2=operand2, expected='int')
        if op == '<':
            opcode = self.program_block.lt
        else:
            opcode = self.program_block.eq
        self.program_block.add_line(opcode, operand1, operand2, temp)
        self.semantic_stack.push(temp)

    def push_size(self, inp):
        var_name = self.semantic_stack.pop()
        var_type = self.semantic_stack.pop()
        assert var_type == 'int'
        var_type = 'array'

        self.semantic_stack.push(inp)
        self.semantic_stack.push(var_type)
        self.semantic_stack.push(var_name)

    def push_size_prime(self, inp):
        var_name = self.semantic_stack.pop()
        var_type = self.semantic_stack.pop()
        assert var_type == 'int'
        var_type = 'array'

        self.semantic_stack.push(None)
        self.semantic_stack.push(var_type)
        self.semantic_stack.push(var_name)

    def push_num(self, inp):
        self.semantic_stack.push(ConstValue(inp))

    def call_function(self, inp):
        args = []
        function = None
        while True:
            top = self.semantic_stack.pop()
            if isinstance(top, FuncSymbol):
                function = top
                break
            args.append(top)
        args = args[::-1]

        assert function is not None

        function.check_arg_types(self, args)
        temp_vars = []
        for item in self.semantic_stack._stack:
            if isinstance(item, TemporaryValue) or isinstance(item, IndirectValue):
                temp_vars.append(item)

        self.run_time_memory.push_func_vars(
            function, caller=self.semantic_stack.first(), temp_vars=temp_vars)
        temp = function.call(self, args)
        self.run_time_memory.pop_func_vars(
            function, caller=self.semantic_stack.first(), temp_vars=temp_vars)
        self.semantic_stack.push(temp)

    def pop(self, inp):
        self.semantic_stack.pop()

    def dec_func(self, inp):
        name = self.semantic_stack.pop()
        return_type = self.semantic_stack.pop()
        func_symbol = self.symbol_table.insert_func(
            scope=self.scope_stack[-1],
            func_symbol=FuncSymbol(
                name=name,
                jump_address=self.program_block.get_current_line() + 1,
                return_address_variable=self.get_new_temporary_address(),
                return_type=return_type,
                return_variable=self.get_new_temporary_address(),
            ),
        )
        if name == 'main':
            self.program_block.change_line(
                1,
                self.program_block.jp,
                self.program_block.get_current_line() + 1,
            )

        self.semantic_stack.push(func_symbol)

    def dec_func_var(self, inp):
        var_name, var_type, var_size = self.get_var_from_stack()
        func_symbol: FuncSymbol = self.semantic_stack.last()

        temp = func_symbol.add_arg(var_name, var_type, var_size, self)
        var_symbol = VarSymbol(
            name=var_name,
            value_type=var_type,
            size=var_size,
            memory_address=temp.address,
            is_indirect=var_type == 'array',
        )
        self.symbol_table.insert_var(
            scope=self.scope_stack[-1],
            var_symbol=var_symbol,
        )
        self.semantic_stack.first().push_variable(var_symbol)

    def action_return(self, inp):
        return_value = self.semantic_stack.pop()
        function: FuncSymbol = self.semantic_stack.first()
        function.do_return(self, return_value)

    def action_no_assign_return(self, inp):
        function: FuncSymbol = self.semantic_stack.first()
        function.do_return(self)

    def get_index(self, inp):
        index = self.semantic_stack.pop()
        value: VarSymbol = self.semantic_stack.pop()
        if value.type != 'array':
            raise ValueTypeMismatchError(message="Bad index.")

        temp = self.get_new_temporary_address()
        # if self.scope_func:
        #     self.scope_func.push_variable(temp)
        self.program_block.add_line(
            self.program_block.mult,
            index,
            ConstValue(4),
            temp,
        )
        self.program_block.add_line(
            self.program_block.add,
            value if value.is_indirect else ConstValue(value.memory_address),
            temp,
            temp,
        )
        self.semantic_stack.push(
            IndirectValue(temp.address)
        )

    def pop_function(self, inp):
        function: FuncSymbol = self.semantic_stack.pop()
        if function.name != 'main':
            function.do_return(self)
