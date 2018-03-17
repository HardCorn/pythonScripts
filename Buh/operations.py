"""Модуль содержит функции для расчета арифметических/логических операций, некоторые константы,
    словарь, задающий соответствие между оператором и а/л функцией, и функцию,
    возвращающую нужную арифметическую/логическую функцию по оператору"""
import re


UNARY_LOGIC_OPERATIONS = ('is none', 'is not none', 'not')
UNARY_ARITHMETIC_OPERATIONS = ()
UNARY_OPERATIONS = UNARY_LOGIC_OPERATIONS + UNARY_ARITHMETIC_OPERATIONS
UNARY_PRE_OPERATIONS = ('is none', 'is not none')
UNARY_POST_OPERATIONS = ('not', )


def less(left, right):
    if left is None or right is None:
        return False
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
    if not (isinstance(left, str) and isinstance(right, str)):
        raise ValueError('Like operator operates only with strings!')
    reg = re.compile(right.replace('_', '.').replace('%', '.*'))
    res = reg.search(left)
    if res is None:
        return False
    else:
        return True


def is_none(variable):
    return variable is None


def is_not_none(variable):
    return variable is not None


def and_(left, right):
    if left is None or right is None:
        return False
    if left == False or right == False:
        return False
    if type(left) != bool or type(right) != bool:
        raise ValueError('Comparison of non-bool variables {0}, {1}'.format(left, right))
    return left and right


def or_(left, right):
    if left is None or right is None:
        return False
    if left == True or right == True:
        return True
    if type(left) != bool or type(right) != bool:
        raise ValueError('Comparison of non-bool variables {0}, {1}'.format(left, right))
    return left or right


def not_(variable):
    if variable is None:
        return False
    if type(variable) != bool:
        raise ValueError('Logic NOT operation not available with {0} operand'.format(variable))
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