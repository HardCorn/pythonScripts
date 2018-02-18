import re

def less(left, right):
    return left < right


def greater(left, right):
    if left is None or right is None:
        return False
    return left > right


def lessequal(left, right):
    if left is None or right is None:
        return False
    return left <= right


def greaterequal(left, right):
    if left is None or right is None:
        return False
    return left >= right


def equal(left, right):
    if left is None or right is None:
        return False
    return left == right


def notequal(left, right):
    if left is None or right is None:
        return False
    return left != right


def in_(left, right):
    if left is None or right is None:
        return False
    return left in right


def not_in(left, right):
    if left is None or right is None:
        return False
    return left not in right


def like(left, right):
    if left is None or right is None:
        return False
    reg = re.compile(right.replace('_', '.').replace('%', '.*'))
    res = reg.search(left)
    if res is None:
        return False
    else:
        return True


def is_none(variable):
    if variable is None:
        return False
    return variable is None


def is_not_none(variable):
    if variable is None:
        return False
    return variable is not None


def and_(left, right):
    if left is None or right is None:
        return False
    return left and right


def or_(left, right):
    if left is None or right is None:
        return False
    return left or right


def not_(variable):
    if variable is None:
        return False
    return not variable


def plus(left, right):
    if left is None or right is None:
        return None
    return left + right


def minus(left, right):
    if left is None:
        return False
    if right is None:
        return -left
    return left - right


def multiply(left, right):
    if left is None or right is None:
        return None
    return left * right


def divide(left, right):
    if left is None or right is None:
        return None
    if right == 0:
        raise ValueError('Arithmetic evaluation: division by zero Error')
    return left / right


def power(left, right):
    if left is None or right is None:
        return None
    return left ** right


OPERATIONS = {
    '<': less,
    '>': greater,
    '=': equal,
    '<=': lessequal,
    '>=': greaterequal,
    '<>': notequal,
    'in': in_,
    'not in': not_in,
    'like': like,
    'and': and_,
    'or': or_,
    'not': not_,
    'is none': is_none,
    'is not none': is_not_none,
    '+': plus,
    '-': minus,
    '*': multiply,
    '/': divide,
    '**': power
}


def get_function(operator):
    return OPERATIONS[operator]


if __name__ == '__main__':
    func = get_function('or')
    print(func(True, False))
    func = get_function('like')
    print(func('some_string', '_ome_string%'))
    import datetime as dt
    func = get_function('>')
    print(func(dt.date(2016,1,3), dt.date(2015, 3,5)))