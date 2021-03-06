class BF:
    KEYS = {"+": 0,
            "-": 1,
            ">": 2,
            "<": 3,
            "[": 4,
            "]": 5,
            ".": 6,
            ",": 7}

    def __init__(self, src="", *, arr=None, ind_var=0, ind_src=0, ind_sts=0):
        self.source = src
        if arr is None:
            arr = [0]
        self.arr = arr
        self.stops = {}
        self.ind_var = ind_var
        self.ind_src = ind_src
        self.ind_sts = ind_sts

    def reset(self, **kwargs):
        self.__init__(self.source, **kwargs)

    def exe(self, go_on=False, **kwargs):
        if not go_on:
            self.reset(**kwargs)
        while self.ind_src < len(self.source):
            self._eval(self.source[self.ind_src])(self)
            self.ind_src += 1

    def debug(self, go_on=False, **kwargs):
        if not go_on:
            self.reset(**kwargs)
        while self.ind_src < len(self.source):
            A = self.arr
            B = self.ind_var
            C = ""
            D = "       "
            E = 3
            if B == 0:
                C = "      " + str(A)
                E = 1
            elif B == 1:
                C = "   " + str(A)
                E = 2
            else:
                C = "~" + str(A[B - 2:])[1:]
            for i in range(1, E):
                if A[B - i] > 99:
                    D = D + "  "
                elif A[B - i] > 9:
                    D = D + " "
            D = D + "^"
            print(C)
            print(D)
            print(self.source[self.ind_src:])
            input()
            self._eval(self.source[self.ind_src])(self)
            self.ind_src += 1

    def _eval(self, char):
        def plus(self):
            self.arr[self.ind_var] += 1
            self.arr[self.ind_var] &= 255

        def minus(self):
            self.arr[self.ind_var] -= 1
            if self.arr[self.ind_var] == -1:
                self.arr[self.ind_var] = 255

        def right(self):
            self.ind_var += 1
            if self.ind_var >= len(self.arr):
                self.arr.append(0)

        def left(self):
            self.ind_var -= 1

        def if_do(self):
            self.ind_sts += 1
            self.stops[self.ind_sts] = self.ind_src
            if not self.arr[self.ind_var]:
                X = self.ind_sts - 1
                while not self.ind_sts == X:
                    self.ind_src += 1
                    if self.KEYS[self.source[self.ind_src]] == 4:
                        self.ind_sts += 1
                    elif self.KEYS[self.source[self.ind_src]] == 5:
                        self.ind_sts -= 1

        def goto(self):
            self.ind_src = self.stops[self.ind_sts] - 1
            self.ind_sts -= 1

        def read(self):
            inp = input() or [chr(0)]
            self.arr[self.ind_var] += ord(inp[0])
            self.arr[self.ind_var] &= 255

        def print_(self):
            print(chr(self.arr[self.ind_var]), end="")

        functions = [plus, minus, right, left, if_do, goto, read, print_]
        return functions[self.KEYS[char]] if char in self.KEYS else lambda x: x

    __call__ = exe
