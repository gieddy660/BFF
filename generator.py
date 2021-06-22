from operators import move, _if, _while


class Expression:
    def __init__(self, inputs, return_positions, code):
        self.inputs = inputs
        self.return_positions = return_positions
        self.code = code

    def compile(self):
        return self.code


class Statement:
    @staticmethod
    def make_unique_name(var_space):
        a = 0
        while (..., a) in var_space:
            a += 1
        return ..., a

    @staticmethod
    def shift_var_space(var_space: dict, delta: int):
        return {x: pos - delta for x, pos in var_space.items()}


class Assignment(Statement):
    # It is assumed that when a statement is executed pointer is at 0 with respect to current var_space
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
        if len(return_positions) != len(self.targets):
            raise Exception('assignment targets must be as many as expression return values')
        for target, return_position in zip(self.targets, return_positions):
            res += move(var_space[target])
            res += move(len(var_space) + return_position, var_space[target])
        return res


class If(Statement):
    def __init__(self, test, body):
        self.test = test
        self.body = body

    def compile(self, var_space):
        t = self.make_unique_name(var_space)
        var_space = dict(var_space) | {t: len(var_space)}  # add a temporary variable, name must be unique

        res = Assignment((t,), self.test).compile(var_space)
        res += '>' * var_space[t]
        res += _if(''.join(statement.compile(self.shift_var_space(var_space, var_space[t])) for statement in self.body))
        res += '<' * var_space[t]

        return res


class While(Statement):
    def __init__(self, test, body):
        self.test = test
        self.body = body

    def compile(self, var_space):
        t = self.make_unique_name(var_space)
        var_space = dict(var_space) | {t: len(var_space)}

        shifted_var_space = self.shift_var_space(var_space, var_space[t])
        test = Assignment((t,), self.test)

        res = test.compile(var_space)
        res += '>' * var_space[t]
        res += _while(''.join(statement.compile(shifted_var_space) for statement in self.body), test.compile(shifted_var_space))
        res += '<' * var_space[t]

        return res


class Scope:
    def __init__(self):
        self.name = None  # optional
        self.var_space = {}
        self.statements = []

    def init_variables(self):
        raise NotImplementedError

    def compile(self):
        return ''.join(statement.compile(self.var_space) for statement in self.statements)

