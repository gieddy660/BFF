import unittest

import operators
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