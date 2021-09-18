import collections.abc
from itertools import zip_longest

from operators import move, _if, _while


class VarSpace(collections.abc.Mapping):
    def __init__(self, iterable=(), sizes=None, *, _len=None):
        # how do i represent arrays?
        # option 1:
        #   I put every cell of the array inside the varspace
        # option 2:
        #   I put arrays in a different table
        # option1 : I don't have to modify varspace / but I can't know array length without iterating
        # option2 : I have to add stuff to varspace / but I can know stuff about arrays more efficiently

        # option 3:
        #   I put every cell of the array inside the varspace
        #   alongside I have a table of the starting position and length of every array
        # option3 : requires more memory / but it's more efficient to retrieve data

        # option 2
        if sizes is None:
            sizes = {}
        self.sizes = sizes
        if isinstance(iterable, collections.abc.Mapping):
            self._dict = dict(iterable)
        else:
            self._dict = {name: position for position, name in enumerate(iterable)}
            acc = 0
            for position, name in enumerate(iterable):
                self._dict[name] = position + acc
                if name in self.sizes:
                    acc += self.sizes[name]
        if _len is None:
            self._len = max(self.values()) + 1
        else:
            self._len = _len

    def __getitem__(self, key):
        if isinstance(key, tuple) and key[0] is not ...:
            return self._dict[key[0]] + key[1]
        return self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return self._len

    def __lshift__(self, delta):
        return VarSpace({x: pos - delta for x, pos in self.items()}, _len=self._len - delta)

    def __or__(self, other):
        if isinstance(other, VarSpace):
            return VarSpace(dict(self) | dict(other), self.sizes | other.sizes)
        return VarSpace(dict(self) | dict(other))

    def add_unique(self, position):
        a = 0
        while (..., a) in self:
            a += 1
        return self | {(..., a): position}, (..., a)


class Expression:
    def __init__(self, inputs, return_positions, code):
        self.inputs = inputs
        self.return_positions = return_positions
        self.code = code

    def compile(self):
        return self.code


class Statement:
    # It is assumed that when a statement is executed pointer is at 0 with respect to current var_space
    pass


class Assignment(Statement):
    # TODO: modify -> target might not be known at compile time
    def __init__(self, targets, expr):
        self.targets = targets
        self.expr = expr

    def compile(self, var_space):
        res = ''
        inputs = self.expr.inputs
        for index, inp in enumerate(inputs):
            res += move(var_space[inp], len(var_space) + index, len(var_space) + index + 1)
            res += move(len(var_space) + index + 1, var_space[inp])

        res += '>' * len(var_space)
        res += self.expr.compile()
        res += '<' * len(var_space)

        return_positions = self.expr.return_positions
        return_positions_var_space = VarSpace()  # maybe put inside expression?
        for return_position in return_positions:
            return_positions_var_space = return_positions_var_space.add_unique(return_position)

        if len(self.targets) > len(return_positions):
            raise Exception("assignment targets can't be more than expression return values")
        for target, return_position in zip_longest(self.targets, return_positions):
            # TODO: put copy_into_array somewhere here
            if isinstance(target, tuple) and not isinstance(target[1], int):
                array, index = target
                t = ((var_space << len(var_space)) | return_positions_var_space) << len(
                    return_positions_var_space)  # this line looks ugly !!!
                d = -t[array]
                res += '>' * (len(var_space) + len(return_positions_var_space))
                res += ''
                res += '<' * (len(var_space) + len(return_positions_var_space))
            elif target is not None:
                res += move(var_space[target])
                res += move(len(var_space) + return_position, var_space[target])
            else:
                res += move(len(var_space) + return_position)
        return res


class If(Statement):
    def __init__(self, test, body):
        self.test = test
        self.body = body

    def compile(self, var_space: VarSpace):
        var_space, t = var_space.add_unique(len(var_space))

        res = Assignment((t,), self.test).compile(var_space)
        res += '>' * var_space[t]
        res += _if(''.join(statement.compile(var_space << var_space[t]) for statement in self.body))
        res += '<' * var_space[t]

        return res


class While(Statement):
    def __init__(self, test, body):
        self.test = test
        self.body = body

    def compile(self, var_space: VarSpace):
        var_space, t = var_space.add_unique(len(var_space))
        test = Assignment((t,), self.test)

        res = test.compile(var_space)
        res += '>' * var_space[t]
        res += _while(''.join(statement.compile(var_space << var_space[t]) for statement in self.body),
                      test.compile(var_space << var_space[t]))
        res += '<' * var_space[t]

        return res


class Scope(Statement):
    def __init__(self, var_space=None, statements=None):
        if var_space is None:
            var_space = VarSpace()
        if statements is None:
            statements = []
        self.var_space = var_space
        self.statements = statements

    def compile(self, var_space=None, init_values=()):
        if var_space is None:
            var_space = VarSpace()
        joined_var_space = (var_space << len(
            var_space)) | self.var_space  # this way the name from the inner scope survives

        res = '>'.join('+' * value for value in init_values) + '<' * len(init_values)
        res += ''.join(statement.compile(joined_var_space) for statement in self.statements)
        return res


class Function:
    def __init__(self, name, scope, parameters, returns):
        self.name = name
        self.scope = scope
        self.parameters = parameters
        self.returns = returns

    def compile(self):
        pass
