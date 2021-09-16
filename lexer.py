import re


def tokenize(text):
    keyword = {'if', 'while', 'def'}
    operator = {'and', 'or', 'not'}
    tokens = {
        'number': r'[0-9]+',
        'string': r'".*"',
        'identifier': r'[_a-zA-Z][_a-zA-Z0-9]*',
        'open_paren': r'\(',
        'close_paren': r'\)',
        'open_array': r'\[',
        'comma': r',',
        'close_array': r'\]',
        'open_scope': r'{',
        'close_scope': r'}',
        'operator': r'[+\-*/%]|==|!=',
        'whitespace': r'[ \t]+',
        'returner': r'\$',
        'newline': r'\n',
        'assignment': r'=',
        'end': r'\.\.\.'
    }
    token_re = '|'.join('(?P<{}>{})'.format(name, pattern) for name, pattern in tokens.items())
    line = 1
    for match in re.finditer(token_re, text):
        kind = match.lastgroup
        value = match.group()
        if kind == 'whitespace':
            continue
        if kind == 'newline':
            line += 1
        if value in operator:
            kind = 'operator'
        if value in keyword:
            kind = 'keyword'
        yield kind, value, line
