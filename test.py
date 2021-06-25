import unittest
from itertools import groupby

import operators
import generator
from interpreter import BF
from lexer import tokenize


class OpTest(unittest.TestCase):
    def test_not(self):
        subtests = [([0], 1), ([1], 0)]
        operator = operators._not
        self.check_operator(subtests, operator)

    def test_or(self):
        subtests = [([0, 0], 0), ([0, 1], 1), ([1, 0], 1), ([1, 1], 1)]
        operator = operators._or
        self.check_operator(subtests, operator)

    def test_and(self):
        subtests = [([0, 0], 0), ([0, 1], 0), ([1, 0], 0), ([1, 1], 1)]
        operator = operators._and
        self.check_operator(subtests, operator)

    def test_add(self):
        subtests = [([a, b], (a + b) % 256) for a in range(256) for b in range(256)]
        operator = operators._add
        self.check_operator(subtests, operator)

    def test_sub(self):
        subtests = [([a, b], ((b - a) % 256 + 256) % 256) for a in range(256) for b in range(256)]
        operator = operators._sub
        self.check_operator(subtests, operator)

    def test_to1(self):
        subtests = [([0], 0)] + [([a], 1) for a in range(1, 256)]
        operator = operators._to1
        self.check_operator(subtests, operator)

    def test_eq(self):
        subtests = [([a, b], int(a == b)) for a in range(256) for b in range(256)]
        operator = operators._eq
        self.check_operator(subtests, operator)

    def test_neq(self):
        subtests = [([a, b], int(a != b)) for a in range(256) for b in range(256)]
        operator = operators._neq
        self.check_operator(subtests, operator)

    def check_operator(self, subtests, operator):
        for subtest in subtests:
            with self.subTest(subtest):
                inp, out = subtest
                op = BF(operator)
                op.exe(arr=inp)
                self.check_final_state(op, out)

    def check_final_state(self, bf_obj, val):
        for index, elem in enumerate(bf_obj.arr):
            if index == 1:
                self.assertEqual(elem, val)
            else:
                self.assertEqual(elem, 0)
        self.assertEqual(bf_obj.ind_var, 0)


class GeneratorTest(unittest.TestCase):
    def test_if(self):
        var_space = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
        add = generator.Assignment(('a',), generator.Expression(('a', 'b'), (1,), operators._add))
        if_ = generator.If(generator.Expression(('c', 'd'), (1,), operators._eq), (add,))
        src = if_.compile(var_space)

        subtests = (([2, 3, 1, 1], [5, 3, 1, 1]), ([4, 7, 1, 1], [11, 7, 1, 1]), ([2, 3, 1, 2], [2, 3, 1, 2]), ([5, 6, 5, 6], [5, 6, 5, 6]))
        self.check_subtests(subtests, src)

    def test_while(self):
        var_space = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
        add = generator.Assignment(('a',), generator.Expression(('a', 'b'), (1,), operators._add))
        decr = generator.Assignment(('c',), generator.Expression(('d', 'c'), (1,), operators._sub))
        while_ = generator.While(generator.Expression(('c',), (1,), operators._to1), (add, decr))
        src = while_.compile(var_space)

        subtests = (([0, 4, 5, 1], [20, 4, 0, 1]), ([5, 5, 5, 1], [30, 5, 0, 1]), ([0, 5, 10, 2], [25, 5, 0, 2]), ([6, 10, 25, 1], [0, 10, 0, 1]))
        self.check_subtests(subtests, src)

    def check_subtests(self, subtests, src):
        for subtest in subtests:
            with self.subTest(msg=f'{subtest}'):
                inp, out = subtest
                program = BF(src)
                program.exe(arr=inp)
                for index, elem in enumerate(program.arr):
                    if index < len(out):
                        self.assertEqual(elem, out[index])
                    else:
                        self.assertEqual(elem, 0)
                self.assertEqual(program.ind_var, 0)


class LexerTest(unittest.TestCase):
    def test_base(self):
        line1 = (('keyword', 'def', 1), ('identifier', 'main', 1), ('open_paren', '(', 1), ('close_paren', ')', 1), ('open_scope', '{', 1))
        line2 = (('newline', '\n', 2), ('identifier', 'a', 2), ('assignment', '=', 2), ('number', '1', 2))
        line3 = (('newline', '\n', 3), ('identifier', 'b', 3), ('open_array', '[', 3), ('number', '3', 3), ('close_array', ']', 3), ('assignment', '=', 3), ('string', '"abc"', 3))
        line4 = (('newline', '\n', 4), ('identifier', 'c', 4), ('assignment', '=', 4), ('number', '3', 4))
        line5 = (('newline', '\n', 5), ('end', '...', 5))
        line6 = (('newline', '\n', 6), ('keyword', 'if', 6), ('identifier', 'a', 6), ('operator', '==', 6), ('identifier', 'b', 6))
        line7 = (('newline', '\n', 7), ('identifier', 'c', 7), ('assignment', '=', 7), ('identifier', 'c', 7), ('operator', '*', 7), ('identifier', 'b', 7))
        line8 = (('newline', '\n', 8), ('end', '...', 8))
        line9 = (('newline', '\n', 9), ('close_scope', '}', 9))
        parsed = (*line1, *line2, *line3, *line4, *line5, *line6, *line7, *line8, *line9)
        with open('test_prog.bff', 'r') as file:
            tokens = tuple(tokenize(file.read()))
            self.assertEqual(tokens, parsed)
