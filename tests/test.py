import unittest

import generator
import operators
from interpreter import BF
from lexer import tokenize


class GeneratorTest(unittest.TestCase):
    def test_var_space(self):
        a = generator.VarSpace('abc', sizes={'c': 2})
        self.assertIsInstance(a, generator.VarSpace)
        self.assertEqual(a['c'], 2)
        self.assertEqual(a['c', 0], 2)
        self.assertEqual(a['c', 1], 3)
        self.assertEqual(len(a), 4)
        b = a << 2
        self.assertIsInstance(b, generator.VarSpace)
        self.assertEqual(b['b'], -1)
        self.assertEqual(b['c', 1], 1)
        self.assertEqual(len(b), 2)
        c = b | {'d': 2, 'e': 3}
        self.assertIsInstance(c, generator.VarSpace)
        self.assertEqual(c['d'], 2)
        self.assertEqual(len(c), 4)
        d, key = c.add_unique()
        self.assertIsInstance(d, generator.VarSpace)
        self.assertNotIn(key, c)
        self.assertIn(key, d)
        self.assertEqual(d[key], len(c))
        self.assertEqual(len(d), len(c) + 1)
        e, key2 = d.add_unique(3)
        self.assertIsInstance(e, generator.VarSpace)
        self.assertNotIn(key2, d)
        self.assertIn(key2, e)
        self.assertEqual(e[key2], len(d))
        self.assertEqual(e[key2, 2], len(d) + 2)
        self.assertEqual(len(e), len(d) + 3)
        f = e << 3
        self.assertIsInstance(f, generator.VarSpace)
        self.assertEqual(f[key2], len(d) - 3)
        self.assertEqual(f[key2, 2], len(d) - 1)
        self.assertEqual(len(f), len(d))

    def test_assignment(self):
        var_space = generator.VarSpace(('a', 'b'))
        add = generator.Assignment(('a',), generator.Expression(('a', 'b'), 1, operators._add))
        src = add.compile(var_space)
        subtests = (([1, 2], [3, 2]), ([3, 4], [7, 4]), ([23, 49], [72, 49]))
        self.check_subtests(subtests, src)

        var_space = generator.VarSpace('abc', sizes={'a': 3})
        add = generator.Assignment((('a', 'b'),), generator.Expression(('b', 'c'), 1, operators._add))
        src = add.compile(var_space)
        subtests = (([0, 0, 0, 0, 3], [3, 0, 0, 0, 3]), ([1, 2, 3, 1, 5], [1, 6, 3, 1, 5]))
        self.check_subtests(subtests, src)

    def test_if(self):
        var_space = generator.VarSpace(('a', 'b', 'c', 'd'))
        add = generator.Assignment(('a',), generator.Expression(('a', 'b'), 1, operators._add))
        if_ = generator.If(generator.Expression(('c', 'd'), 1, operators._eq), (add,))
        src = if_.compile(var_space)

        subtests = (([2, 3, 1, 1], [5, 3, 1, 1]), ([4, 7, 1, 1], [11, 7, 1, 1]), ([2, 3, 1, 2], [2, 3, 1, 2]),
                    ([5, 6, 5, 6], [5, 6, 5, 6]))
        self.check_subtests(subtests, src)

    def test_while(self):
        var_space = generator.VarSpace(('a', 'b', 'c', 'd'))
        add = generator.Assignment(('a',), generator.Expression(('a', 'b'), 1, operators._add))
        decr = generator.Assignment(('c',), generator.Expression(('c', 'd'), 1, operators._sub))
        while_ = generator.While(generator.Expression(('c',), 1, operators._to1), (add, decr))
        src = while_.compile(var_space)
        print(len(src), src)

        subtests = (([0, 4, 5, 1], [20, 4, 0, 1]), ([5, 5, 5, 1], [30, 5, 0, 1]), ([0, 5, 10, 2], [25, 5, 0, 2]),
                    ([6, 10, 25, 1], [0, 10, 0, 1]))
        self.check_subtests(subtests, src)

    def check_subtests(self, subtests, src):
        for subtest in subtests:
            with self.subTest(msg=f'{subtest}'):
                inp, out = subtest
                program = BF(src)
                program.exe(arr=inp)
                print(program.arr, out)
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
        line3 = (('newline', '\n', 3), ('identifier', 'b', 3), ('open_array', '[', 3), ('number', '3', 3),
                 ('close_array', ']', 3), ('assignment', '=', 3), ('string', '"abc"', 3))
        line4 = (
        ('newline', '\n', 4), ('returner', '$', 4), ('identifier', 'c', 4), ('assignment', '=', 4), ('number', '3', 4))
        line5 = (('newline', '\n', 5), ('end', '...', 5))
        line6 = (('newline', '\n', 6), ('keyword', 'if', 6), ('identifier', 'a', 6), ('operator', '==', 6), ('identifier', 'b', 6))
        line7 = (('newline', '\n', 7), ('identifier', 'c', 7), ('assignment', '=', 7), ('identifier', 'c', 7), ('operator', '*', 7), ('identifier', 'b', 7))
        line8 = (('newline', '\n', 8), ('end', '...', 8))
        line9 = (('newline', '\n', 9), ('close_scope', '}', 9))
        expected = (*line1, *line2, *line3, *line4, *line5, *line6, *line7, *line8, *line9)
        with open('test_prog.bff', 'r') as file:
            actual = tuple(tokenize(file.read()))
            self.assertEqual(actual, expected)
