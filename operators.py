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


_not = '[->-<]>+<'
_or = '[' + move(1) + move(0, 1) + ']'
_and = move(1, 2) + '[-' + move(2, 1) + ']' + move(2)

_add = move(0, 1)
_sub = move(0, (1, -1))
_mul = move(1, 3) + '[-' + move(3, 1, 2) + move(2, 3) + ']' + move(3)
