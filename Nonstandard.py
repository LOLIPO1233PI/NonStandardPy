from decimal import Decimal
from fractions import Fraction
from math import prod
from numbers import Number
from typing import Any, Union


translation_table = {
    45: 8315,
    48: 8304,
    49: 185,
    50: 178,
    51: 179,
    52: 8308,
    53: 8309,
    54: 8310,
    55: 8311,
    56: 8312,
    57: 8313,
    47: 8260,
}


def devellop_tuple(A: tuple[Any]) -> list[Any]:
    # [(..ε, ...ε), (...ε^n, ...ε^n)]
    operation_res = []
    K1, K2 = A
    for i in K1:
        for x in K2:
            operation_res.append(x * i)
    return operation_res

def make_list_same(a, b):
    if len(b) < len(a):
        b = [*b, *[1 for _ in range(len(a) - len(b))]]
    elif len(b) > len(a):
        a = [*a, *[1 for _ in range(len(b) - len(a))]]
    return (a, b)


# this is the same as str.maketrans("-0123456789/", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹⁄")
def super_script(value: Number) -> str:
    return str(value).translate(translation_table)


# taken from one of my older projects :) so feel free to do what ever you wont !
def valid_input(
    N: Union[int, Decimal, Fraction, float], max_precision: int = 10**14
) -> Union[int, Fraction]:
    if isinstance(N, (int,Fraction)):
        return N
    elif isinstance(N, Decimal):
        return Fraction.from_decimal(N).limit_denominator(max_precision)
    elif isinstance(N, float):
        return Fraction.from_float(N).limit_denominator(max_precision)
    elif isinstance(N, (HyperRealExp, Epsilon)):
        return N


class Epsilon:
    __slots__ = ("value", "exp")

    def __init__(self, quantity, exp=1):
        self.value = valid_input(quantity)
        self.exp = valid_input(exp)

    def __str__(self):
        if self.value == 0:
            return "0"
        elif self.exp == 0:
            return str(self.value)
        elif self.exp < 0:
            return f'{self.value}ω{super_script(-self.exp) if self.exp != -1 else ''}' # so we dont need to add an actuall omega class
        return f"{self.value}ε{super_script(self.exp) if self.exp != 1 else ''}"

    def __repr__(self):
        return str(self)

    def __mul__(self, value):
        if isinstance(value, self.__class__):
            return Epsilon(value.value * self.value, self.exp + value.exp)
        return Epsilon(valid_input(value) * self.value, self.exp)

    def __rmul__(self, value):
        return self * value

    def __add__(self, value):
        if isinstance(value, self.__class__):
            if value.exp == self.exp == 1:
                return Epsilon(value.value + self.value, self.exp)
        elif value == 0:
            return self
        return HyperRealExp(self, valid_input(value))

    def __radd__(self, value):
        return self + value

    def __pow__(self, value):
        value = valid_input(value)
        return Epsilon(self.value**value, self.exp * value)

    def __truediv__(self, value):
        if isinstance(value, self.__class__):
            return Epsilon(Fraction(self.value, value.value), self.exp - value.exp)
        return Epsilon(Fraction(self.value, valid_input(value)), self.exp)

    def __rtruediv__(self, value):
        return Epsilon(Fraction(valid_input(value), self.value), -self.exp)

    def __pos__(self):
        return self

    def __neg__(self):
        return Epsilon(-self.value, self.exp)

    def st(self) -> Number:
        return self.value

    def simplify(self):
        return 0 if self.value == 0 else (self.value if self.exp == 0 else self)

    def __eq__(self, value):
        if isinstance(value, Epsilon):
            return value.value == self.value and self.exp == value.exp
        return False

    def __sub__(self, value):
        return self + -value
    
    def __rsub__(self, value):
        return value + -self
class HyperRealExp:
    __slots__ = ("expresion", "real_part", "hyper_real_part")

    def __init__(self, *args):
        self.expresion = [*args]
        
        self.real_part = sum([i for i in self.expresion if isinstance(i, Number)])
        # filtering for hyperreals
        self.hyper_real_part: object = list(
            [i for i in self.expresion if isinstance(i, (Epsilon,))]
        )
        
        self.hyper_real_part = [i.simplify() for i in self.hyper_real_part]
    
        self.real_part = sum(
            [
                self.real_part,
                *[i for i in self.hyper_real_part if isinstance(i, Number)],
            ]
        )
        self.hyper_real_part = [i for i in self.hyper_real_part if isinstance(i, Epsilon)]
        
        infinitesimal_exp_table = set([i.exp for i in self.hyper_real_part])
        # separating them by exponent
        
        hyper_parts = [
            list(filter(lambda x: x.exp == i, self.hyper_real_part))
            for i in infinitesimal_exp_table
        ]
        self.hyper_real_part = [sum(i) for i in hyper_parts]

        self.expresion = [self.real_part, *self.hyper_real_part]

    def __str__(self):
        if not self.hyper_real_part:
            return str(self.real_part)
        return f"{self.real_part} + {' + '.join(map(str, self.hyper_real_part))}"

    def __mul__(self, value):
        value = valid_input(value)
        if isinstance(value, HyperRealExp):
            return HyperRealExp(
                self.real_part * value.real_part,
                *devellop_tuple(make_list_same(self.hyper_real_part, value.hyper_real_part)), # this were is located the problem
                *[i * self.real_part for i in value.hyper_real_part],
                *[i * value.real_part for i in self.hyper_real_part],
            )
        return HyperRealExp(
            self.real_part * value,
            *[i * value for i in self.hyper_real_part],
        )

    def __rmul__(self, value):
        return self * value

    def __add__(self, value):
        value = valid_input(value)
        return HyperRealExp(*self.expresion, value)

    def __radd__(self, value):
        return self + value

    def __sub__(self, value):
        value = valid_input(value)
        return HyperRealExp(*self.expresion, -value)

    def __truediv__(self, value):
        if isinstance(value, Epsilon):
            return HyperRealExp(
                self.real_part / value,
                *[i / value for i in self.hyper_real_part],
            )
        
        return self * (Fraction(1, valid_input(value)))

    def __pow__(self, value):
        if isinstance(value, int):
            return prod([self for _ in range(value)])
        return NotImplementedError

    # 
    def st(self):
        return self.real_part

    def __eq__(self, value):
        if isinstance(value, HyperRealExp):
            return self.real_part == value.real_part and self.hyper_real_part == value.hyper_real_part
        return False

    def MD(self, MDfileName: str = "MathOut.md") -> None:
        Content = f'* {str(self)}\n'
        with open(MDfileName, "a", encoding='utf-8') as f:
            f.write(Content)
        print(f'This expression has been exported to {MDfileName}')

if __name__ == "__main__":
    print((Epsilon(1) - 5 - Epsilon(1, 2)))
    (Epsilon(1) - 5 - Epsilon(1, 2)).MD() # (ε - 5)(ε - 5)
    #