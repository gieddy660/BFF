from operators import move, _if


class Expression:
    def __init__(self, inputs, return_positions, code):
        self.inputs = inputs
        self.return_positions = return_positions
        self.code = code

    def compile(self):
        return self.code


class Statement:
    pass


class Assignment(Statement):
    # It is assumed that when a statement is executed pointer is at 0 with respect to current var_space
    def __init__(self, target, expr):
        self.target = target
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
        for return_position in return_positions:
            res += move(var_space[self.target])
            res += move(len(var_space) + return_position, var_space[self.target])
        return res


class If(Statement):
    def __init__(self, test, body):
        # test should return a bool (either 0 or 1) but I don't really know how to enforce this
        self.test = test
        self.body = body

    @staticmethod
    def make_unique_name():
        return ...

    def compile(self, var_space):
        t = self.make_unique_name()
        var_space = dict(var_space) | {t: len(var_space)}  # add a temporary variable, name must be unique
        res = Assignment(t, self.test).compile(var_space)

        res += '>' * var_space[t]
        res += _if('<' * var_space[t] + ''.join(statement.compile(var_space) for statement in self.body) + '>' * var_space[t])
        res += '<' * var_space[t]

        return res


class While(Statement):
    def __init__(self, test, body):
        self.test = test
        self.body = body


class Scope:
    def __init__(self):
        self.name = None  # optional
        self.var_space = {}
        self.statements = []

    def init_variables(self):
        raise NotImplementedError

    def compile(self):
        return ''.join(statement.compile(self.var_space) for statement in self.statements)

