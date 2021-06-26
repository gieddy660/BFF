import collections.abc
from itertools import zip_longest

from operators import move, _if, _while


class VarSpace(collections.abc.Mapping):
    def __init__(self, iterable=(), *, _len=None):
        if isinstance(iterable, collections.abc.Mapping):
            self._dict = dict(iterable)
        else:
            self._dict = {name: position for position, name in enumerate(iterable)}
        if _len is None:
            self._len = max(self.values()) + 1
        else:
            self._len = _len

    def __getitem__(self, key):
        return self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return self._len

    def __lshift__(self, delta):
        return VarSpace({x: pos - delta for x, pos in self.items()}, _len=self._len - delta)

    def __or__(self, other):
        return VarSpace(dict(self) | dict(other))

    def add_unique(self):
        a = 0
        while (..., a) in self:
            a += 1
        return self | {(..., a): self._len}, (..., a)


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
        if len(self.targets) > len(return_positions):
            raise Exception("assignment targets can't be more than expression return values")
        for target, return_position in zip_longest(self.targets, return_positions):
            if target is not None:
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
        var_space, t = var_space.add_unique()

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
        var_space, t = var_space.add_unique()
        test = Assignment((t,), self.test)

        res = test.compile(var_space)
        res += '>' * var_space[t]
        res += _while(''.join(statement.compile(var_space << var_space[t]) for statement in self.body),
                      test.compile(var_space << var_space[t]))
        res += '<' * var_space[t]

        return res


class Scope:
    def __init__(self):
        self.name = None  # optional
        self.var_space = {}
        self.statements = []

    def init_variables(self):
        raise NotImplementedError

    def compile(self, var_space=None):
        if var_space is None:
            var_space = VarSpace()
        joined_var_space = (var_space << len(
            var_space)) | self.var_space  # this way the name from the inner scope survives
        return ''.join(statement.compile(joined_var_space) for statement in self.statements)
