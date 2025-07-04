from decimal import Decimal
from fractions import Fraction
from math import prod
from numbers import Number
from typing import Self, Union, List


class SupportsAdd:
    "Type hinting for class wich have a deffined addition operation"

translation_table = str.maketrans("-0123456789/", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹⁄")


def super_script(value: Number) -> str:
    "Turn a number into it's superscript counterpart, Ex: 2 -> ²"
    return str(value).translate(translation_table)


# taken from one of my older projects :) so feel free to do what ever you wont !
def valid_input(
    N: Union[Number, "Omega", "Epsilon", "HyperRealExp"],
    max_precision: int = 10**14,
) -> Union[int, Fraction, "Omega", "Epsilon", "HyperRealExp"]:
    "Simple input validation for precision sake"
    if isinstance(N, Decimal):
        return Fraction.from_decimal(N).limit_denominator(max_precision)
    elif isinstance(N, float):
        return Fraction.from_float(N).limit_denominator(max_precision)
    return N


def develop_list(A: List[SupportsAdd], B: List[SupportsAdd]) -> List[SupportsAdd]:
    # [...ε^n, ...ε^n, ...], [...ε^n, ...ε^n, ...]
    operation_res = []
    K1, K2 = A, B
    for i in K1:
        for x in K2:
            operation_res.append(x * i)
    return operation_res


class Epsilon:
    "A class that mimics the behavior of a infinitesimal"

    __slots__ = ("value", "exp")

    def __new__(cls, q: Number = 1, exp: Number = 1) -> Self | Number:
        return 0 if q == 0 else (q if exp == 0 else super().__new__(cls))

    # simplifiying then return object (self) and forwaring the logic to the
    # the __new__ dunder is really new for me so i didn't comprehend it well

    def __init__(self, quantity: Number, exp: Number = 1) -> None:
        self.value = valid_input(quantity)
        self.exp = valid_input(exp)

    def __str__(self) -> str:
        if self.exp < 0:
            return (
                (str(self.value) if self.value != 1 else "")
                + "ω"
                + (super_script(-self.exp) if self.exp != -1 else "")
            )  # so we dont need to add an actuall omega class
        return (
            (str(self.value) if self.value != 1 else "")
            + "ε"
            + (super_script(self.exp) if self.exp != -1 else "")
        )

    def __repr__(self) -> str:
        return str(self)

    def __mul__(self, value) -> "Epsilon":
        if isinstance(value, self.__class__):
            return Epsilon(value.value * self.value, self.exp + value.exp)
        return Epsilon(valid_input(value) * self.value, self.exp)

    def __rmul__(self, value) -> "Epsilon":
        return self * value

    def __add__(self, value) -> Self | "HyperRealExp" | "Epsilon":
        if isinstance(value, self.__class__):
            if value.exp == self.exp:
                return Epsilon(value.value + self.value, self.exp)
        elif value == 0:
            return self
        return HyperRealExp(self, valid_input(value))

    def __radd__(self, value) -> Self | "HyperRealExp" | "Epsilon":
        return self + value

    def __pow__(self, value) -> "Epsilon":
        value = valid_input(value)
        return Epsilon(self.value**value, self.exp * value)

    def __truediv__(self, value) -> "Epsilon":
        if isinstance(value, self.__class__):
            return Epsilon(Fraction(self.value, value.value), self.exp - value.exp)
        return Epsilon(Fraction(self.value, valid_input(value)), self.exp)

    def __rtruediv__(self, value) -> "Epsilon":
        return Epsilon(Fraction(valid_input(value), self.value), -self.exp)

    def __pos__(self) -> Self:
        return self

    def __neg__(self) -> "Epsilon":
        return Epsilon(-self.value, self.exp)

    def st(self) -> int | Fraction:
        return self.value

    def simplify(self) -> int | Fraction | Self:
        return 0 if self.value == 0 else (self.value if self.exp == 0 else self)

    def __eq__(self, value) -> bool:
        if isinstance(value, Epsilon):
            return value.value == self.value and self.exp == value.exp
        return False

    def __sub__(self, value) -> Self | "HyperRealExp" | "Epsilon":
        return self + -value

    def __rsub__(self, value) -> Self | "HyperRealExp" | "Epsilon":
        return value + -self

    def MD(self, MDfileName: str = "MathOut.md") -> None:
        Content = "* {}".format(str(self)) + "\n \n"
        with open(MDfileName, "a", encoding="utf-8") as f:
            f.write(Content)
        print("This expression has been exported to %s ", MDfileName)


class Omega:
    "A class that mimics the behavior of infinities"

    def __new__(cls, q: Number = 1, exp: Number = 1) -> Epsilon:
        return Epsilon(q, -exp)


class HyperRealExp:
    "A hyperreal expression object wich has a real part and a hyperreal part, Ex: 1 + ε"

    __slots__ = ("expresion", "real_part", "hyper_real_part")

    def __init__(self, *args):
        self.expresion = [*args]

        self.real_part = sum([i for i in self.expresion if isinstance(i, Number)])
        # filtering for hyperreals
        self.hyper_real_part: object = [
            i for i in self.expresion if isinstance(i, (Epsilon,))
        ]

        infinitesimal_exp_table = {*[i.exp for i in self.hyper_real_part]}
        # separating them by exponent
        
        hyper_parts = [
            [x for x in self.hyper_real_part if x.exp == i]
            for i in infinitesimal_exp_table
        
        ]
        self.hyper_real_part = [sum(i) for i in hyper_parts]

        self.expresion = [self.real_part, *self.hyper_real_part]

    def __str__(self) -> str:
        if not self.hyper_real_part:
            return str(self.real_part)
        elif self.real_part == 0:
            return " + ".join(map(str, self.hyper_real_part))
        return str(self.real_part) + " + " + " + ".join(map(str, self.hyper_real_part))

    def __mul__(self, value) -> "HyperRealExp":
        value = valid_input(value)
        if isinstance(value, HyperRealExp):
            return HyperRealExp(
                self.real_part * value.real_part,
                *develop_list(
                    self.hyper_real_part, value.hyper_real_part
                ),
                *[i * self.real_part for i in value.hyper_real_part],
                *[i * value.real_part for i in self.hyper_real_part],
            )
        return HyperRealExp(
            self.real_part * value,
            *[i * value for i in self.hyper_real_part],
        )

    def __rmul__(self, value) -> "HyperRealExp":
        return self * value

    def __add__(self, value) -> "HyperRealExp":
        value = valid_input(value)
        return HyperRealExp(*self.expresion, value)

    def __radd__(self, value) -> "HyperRealExp":
        return self + value

    def __sub__(self, value) -> "HyperRealExp":
        value = valid_input(value)
        return HyperRealExp(*self.expresion, -value)

    def __truediv__(self, value) -> "HyperRealExp":
        if isinstance(value, Epsilon):
            return HyperRealExp(
                self.real_part / value,
                *[i / value for i in self.hyper_real_part],
            )

        return self * (Fraction(1, valid_input(value)))

    def __pow__(self, value) -> "HyperRealExp":
        if isinstance(value, int):
            if value < 0:
                return prod([self for _ in range(value)])
            return prod([self for _ in range(value)])
        return NotImplemented

    def st(self) -> int | Fraction:
        return self.real_part

    def __eq__(self, value) -> bool:
        if isinstance(value, HyperRealExp):
            return (
                self.real_part == value.real_part
                and self.hyper_real_part == value.hyper_real_part
            )
        return False

    def MD(self, MDfileName: str = "MathOut.md") -> None:
        Content = "* {}".format(str(self)) + "\n \n"
        with open(MDfileName, "a", encoding="utf-8") as f:
            f.write(Content)
        print("This expression has been exported to %s ", MDfileName)
        
if __name__ == "__main__":
    print(((Epsilon(1) + Epsilon(2, -1)) ** 2))
