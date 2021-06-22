import unittest

import operators
import generator
from interpreter import BF


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
