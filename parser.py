import generator


def build_program(tokens):
    # outermost there can only be function definitions
    functions_table = {}
    while tokens:
        kind, value, line = next(iter(tokens))
        if kind != 'keyword' or value != 'def':
            raise SyntaxError(f'You can only define functions in global space: {line}')
        function, token = build_function(tokens)
        functions_table[function.name] = function
    return functions_table


def build_function(tokens):
    # functions have a name, parameters, and a scope
    name = ''
    parameters = ()

    scope, tokens = build_scope(tokens)
    return generator.Function(name, scope, parameters), tokens


def build_scope(tokens):
    # scopes are divided in two parts: declarations and statements, separated by ...
    # also declarations creates varspace
    return generator.Scope, tokens


def build_statement(tokens):
    # there exist four kinds of statements: assignment, if, else, scope; separated by newlines
    pass


def build_assignment(tokens):
    # assigmnent is of the form: target(s) of the assigmnent (separated by commas) = expression
    pass


def builf_if(tokens):
    pass


def builf_while(tokens):
    pass


def build_expression(tokens):
    # expression = expression op expression /oppure/ f(expression, expression, expression) /oppure/ identifier /oppure/ const /oppure/
    pass


def resolve_identifier(tokens):
    identifier = ''
    for kind, value, line in tokens:
        if kind == 'identifier':
            identifier = value
        elif kind == 'open_array':
            pass


def build_expression(tokens):
    return NotImplemented


def build_assignment(tokens):
    targets = []
    for kind, value, line in tokens:
        if kind == 'identifier':
            targets += value
        if kind == 'assignment':
            break
    expr = build_expression(tokens)
    return generator.Assignment(targets, expr)


def build_if(tokens):
    targets = []


def build_scope(tokens):
    declarations = []
    decl_or_body = 'decl'

    for kind, value, line in tokens:
        pass


def parse(tokens):
    expression = r'identifier operator identifier|identifier(*identifier)'
    declaration = r'identifier([size])?=number|(number,)+|string'
    assigmnet = r'identifier*,*=expression\n'
    if_ = r'if(?expression)?\nstatement*...\n'
    while_ = r'while(?expression)?\nstatement*...\n'
    scope = r'{declaration*...\nstatement*}\n'
    function = r'def identifier(identifier*)scope'
