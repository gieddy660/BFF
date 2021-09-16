# pointer starts at 0 and ends at 0

def move(inp, *out):
    # starting at 0 (absolute or relative depending on context)
    res = ('>' if inp >= 0 else '<') * abs(inp)
    position = inp
    res += '[-'
    for element in out:
        try:
            target_position, multiplier = element
        except TypeError:
            target_position, multiplier = element, 1
        relative_move = target_position - position
        res += ('>' if relative_move >= 0 else '<') * abs(relative_move)
        res += ('+' if multiplier >= 0 else '-') * abs(multiplier)
        position = target_position
    relative_move = inp - position
    res += ('>' if relative_move >= 0 else '<') * abs(relative_move)
    res += ']'
    res += ('>' if -inp >= 0 else '<') * abs(-inp)
    return res


# Control flow
def _if(something):
    """we expect the boolean value if acts according to to be at position 0"""
    return '[[-]' + something + ']'


def _while(something, valuate):
    """we expect the expression to valuate to be at position 0"""
    return '[' + something + valuate + ']'


def _copy_from_array(arr0, arr_size):
    """The variable with the index will be at the end of the VarSpace - which will be called position 0.
    Therefore arr0 will be a negative number. It copies the value to position 1."""
    cycle1 = '[->>+<<' + move(arr0, 3)
    for i in range(arr_size - 1):
        cycle1 += move(arr0 + i + 1, arr0 + i)
    cycle1 += move(3, arr0 + arr_size) + ']'

    copy_res = move(arr0, 1, 3) + move(3, arr0)

    cycle2 = '[>>-<<' + move(arr0 + arr_size, 3)
    for i in range(arr_size - 1):
        cycle2 += move(arr0 + arr_size - i - 1, arr0 + arr_size - i)
    cycle2 += move(3, arr0) + ']'

    return cycle1 + copy_res + cycle2


# Operations
# result in 1

_noop = ''

_not = '[->-<]>+<'
_or = '[' + move(1) + move(0, 1) + ']'
_and = move(1, 2) + '[-' + move(2, 1) + ']' + move(2)

_add = move(0, 1)
_sub = move(0, (1, -1))
_mul = move(1, 3) + '[-' + move(3, 1, 2) + move(2, 3) + ']' + move(3)
_div = NotImplemented  # yet
_mod = NotImplemented  # yet

_to1 = '[>+<' + move(0) + ']'
_neq = move(1, (0, -1)) + _to1
_eq = _neq + move(1, 0) + _not

#
#

_copy_from_distance = '[->+<' + move(-1, 3) + move(0, -1) + move(1, 0) + '<]' \
                      + move(-1, 2, 3) + move(3, -1) \
                      + '>[-' + move(3, -1) + move(1, 2) + move(0, 1) + '>]'

_copy_into_distance = '[->+<' + move(-1, 3) + move(0, -1) + move(1, 0) + move(2, 1) + '<]' \
                      + move(-1) + move(2, -1) \
                      + '>[-' + move(3, -1) + move(0, 1) + '>]'
