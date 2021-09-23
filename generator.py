# TODO: testing

import collections.abc
from itertools import zip_longest

from operators import move, _if, _while, _sub, _copy_into_distance


class VarSpace(collections.abc.Mapping):
    def __init__(self, iterable=(), sizes=None, *, _len=None):
        if sizes is None:
            sizes = {}
        self.sizes = sizes
        if isinstance(iterable, collections.abc.Mapping):
            self._dict = dict(iterable)
        else:
            self._dict = {}
            acc = 0
            for position, name in enumerate(iterable):
                self._dict[name] = position + acc
                acc += self.sizes.get(name, 1) - 1
        if _len is None:
            self._len = max(pos + self.sizes.get(name, 1) for name, pos in self.items())
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

    def add_unique(self, size=1):
        a = 0
        while (..., a) in self:
            a += 1
        return self | VarSpace({(..., a): len(self)}, sizes={(..., a): size}), (..., a)


class Expression:
    def __init__(self, sub_expressions, n_returns, operation):
        self.sub_expressions = sub_expressions
        self.n_returns = n_returns
        self.operation = operation

    @staticmethod
    def enumerate(iterable):
        t = 0
        for element in iterable:
            if isinstance(t, Expression):
                yield t, element
                t += element.n_returns
            else:
                yield t, element
                t += 1

    def compile(self, var_space: VarSpace):
        res = ''
        for index, sub_expression in self.enumerate(self.sub_expressions):
            t = len(var_space) + index
            if isinstance(sub_expression, int):
                res += '>' * t
                res += '+' * sub_expression
                res += '<' * t
            elif isinstance(sub_expression, Expression):
                var_space1, _ = var_space.add_unique(index)
                res += sub_expression.compile(var_space1)
            else:  # if it is a variable
                res += move(var_space[sub_expression], t, t + 1)
                res += move(t + 1, var_space[sub_expression])
        res += '>' * len(var_space)
        try:
            res += self.operation.compile(var_space << len(var_space))
        except AttributeError:
            res += self.operation
        res += '<' * len(var_space)
        return res


class Statement:
    # It is assumed that when a statement is executed pointer is at 0 with respect to current var_space
    pass


class Assignment(Statement):
    def __init__(self, targets, expr):
        self.targets = targets
        self.expr = expr

    def compile(self, var_space):
        res = self.expr.compile(var_space)

        if len(self.targets) > self.expr.n_returns:
            raise Exception("assignment targets can't be more than expression return values")
        for target, return_position in zip_longest(self.targets, range(self.expr.n_returns)):
            position = len(var_space) + return_position
            if isinstance(target, tuple) and not isinstance(target[1], int):
                array, index = target

                var_space1, name = var_space.add_unique(self.expr.n_returns)
                name = (name, return_position)
                var_space2 = var_space1 << len(var_space1)

                res += '>' * len(var_space1)
                t = Expression((-var_space2[array] - 1, index), 1, _sub)  # distance
                res += Expression((t, name), 0, _copy_into_distance).compile(var_space2)
                res += move(var_space2[name])
                res += '<' * len(var_space1)
            elif target is not None:
                res += move(var_space[target])
                res += move(position, var_space[target])
            else:
                res += move(position)
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


class Scope(Statement):
    def __init__(self, var_space=None, statements=None, init_values=(), returns=()):
        if var_space is None:
            var_space = VarSpace()
        if statements is None:
            statements = []
        self.var_space = var_space
        self.statements = statements
        self.init_values = init_values
        self.returns = returns

    def compile(self, external_var_space=None):
        if external_var_space is None:
            external_var_space = VarSpace()
        joined_var_space = (external_var_space << len(external_var_space)) | self.var_space
        res = '>' * len(external_var_space)
        res += '>'.join('+' * value for value in self.init_values) + '<' * (len(self.init_values) - 1)
        res += ''.join(statement.compile(joined_var_space) for statement in self.statements)

        t = 0
        for pos in range(len(self.var_space)):
            if pos in self.returns and t != pos:
                res += move(pos, t)
                t += 1
            elif pos not in self.returns:
                res += move(pos)

        res += '<' * len(external_var_space)
        return res


class Function:
    def __init__(self, name, scope, parameters):
        self.name = name
        self.scope = scope
        self.parameters = parameters
        self.returns = len(scope.returns)

    def compile(self):
        param_var_space = VarSpace(self.parameters)
        res = self.scope.compile(param_var_space)

        if self.parameters:
            for pos in range(self.returns):
                res += move(pos + len(self.parameters), pos)
        return res
