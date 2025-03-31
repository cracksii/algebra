from math import e, factorial
from term import Term

# ALL TRIGONOMETRIC FUNCTIONS ARE IN DEGREES ° !!!

def sqrt(x):
    return nthrt(x, 2)


def nthrt(x, n):
    return x ** (1 / n)


def exp(x):
    return e ** x


def pow(base, exp):
    return base ** exp


# TODO
def fac(x):
    return factorial(x)


def sin(x):
    x = Term(x)
    x.instructions.append(('rsin', 0))
    return x


def cos(x):
    x.instructions.append(('rcos', 0))
    return x


def tan(x):
    x.instructions.append(('rtan', 0))
    return x

def arcsin(x):
    x.instructions.append(('rasin', 0))
    return x

def arccos(x):
    x.instructions.append(('racos', 0))
    return x

def arctan(x):
    x.instructions.append(('ratan', 0))
    return x

