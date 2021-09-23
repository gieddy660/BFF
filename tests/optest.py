import unittest
from itertools import zip_longest

import operators
from interpreter import BF


class OpTest(unittest.TestCase):
    def check_operator(self, subtests, operator, zero_position=0):
        for subtest in subtests:
            with self.subTest(subtest):
                inp, out = subtest
                op = BF(operator)
                op.exe(arr=inp, ind_var=zero_position)
                self.check_final_state(op, out, zero_position)

    def check_final_state(self, bf_obj, val, zero_position):
        for index, elem in enumerate(bf_obj.arr):
            if index < zero_position:
                pass
            elif index == zero_position:
                self.assertEqual(elem, val)
            else:
                self.assertEqual(elem, 0)
        self.assertEqual(bf_obj.ind_var, zero_position)


class LogicOpTest(OpTest):
    def test_to1(self):
        subtests = [([0], 0)] + [([a], 1) for a in range(1, 256)]
        operator = operators._to1
        self.check_operator(subtests, operator)

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


class ArithmeticOpTest(OpTest):
    def test_add(self):
        subtests = [([a, b], (a + b) % 256) for a in range(256) for b in range(256)]
        operator = operators._add
        self.check_operator(subtests, operator)

    def test_sub(self):
        subtests = [([a, b], ((a - b) % 256 + 256) % 256) for a in range(256) for b in range(256)]
        operator = operators._sub
        self.check_operator(subtests, operator)

    def test_mul(self):
        subtests = [([a, b], (a * b) % 256) for a in range(32) for b in range(32)]
        operator = operators._mul
        self.check_operator(subtests, operator)


class CompareOpTest(OpTest):
    def test_eq(self):
        subtests = [([a, b], int(a == b)) for a in range(256) for b in range(256)]
        operator = operators._eq
        self.check_operator(subtests, operator)

    def test_neq(self):
        subtests = [([a, b], int(a != b)) for a in range(256) for b in range(256)]
        operator = operators._neq
        self.check_operator(subtests, operator)


class ArrTest(OpTest):
    def test_copy_from_distance(self):
        def t(num):
            arr = [1, 2, 3, 0, 4, 5, 6]
            return arr + [num]

        subtests = [(t(0), t(6)), (t(1), t(5)), (t(2), t(4)), (t(3), t(0)), (t(4), t(3)), (t(5), t(2)), (t(6), t(1))]
        zero_position = 7
        operator = operators._copy_from_distance
        self.check_operator(subtests, operator, zero_position)

    def test_copy_into_distance(self):
        arr = [1, 2, 3, 0, 4, 5, 6]
        val = 237

        def i(num):
            return arr + [num] + [val]

        def o(num):
            _arr = arr.copy()
            _arr[num] = val
            return _arr

        subtests = [(i(0), o(6)), (i(1), o(5)), (i(2), o(4)), (i(3), o(3)), (i(4), o(2)), (i(5), o(1)), (i(6), o(0))]
        zero_position = 7
        operator = operators._copy_into_distance
        self.check_operator(subtests, operator, zero_position)

    def check_final_state(self, bf_obj, target, zero_position):
        print(target, bf_obj.arr)
        for expected, actual in zip_longest(target, bf_obj.arr, fillvalue=0):
            self.assertEqual(expected, actual)
        self.assertEqual(bf_obj.ind_var, zero_position)
