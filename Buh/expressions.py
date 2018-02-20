import modelExceptions as er
import dates as dt
import operations as op


COMPARE_OPERATOR_LIST = ('<', '>', '=', '<=', '>=', '<>', 'in', 'not in', 'like', 'is none', 'is not none')
BOOL_OPERATOR_LIST = ('and', 'or', 'not')
LOGIC_OPERATOR_LIST = COMPARE_OPERATOR_LIST + BOOL_OPERATOR_LIST
ARITHMETIC_OPERATOR_LIST = ('+', '-', '*', '/', '**')
CONTROL_OPERATOR_LIST = ('(', ')')
COMMA_OPERATOR = (',',)
OPERATOR_LIST = LOGIC_OPERATOR_LIST + ARITHMETIC_OPERATOR_LIST + CONTROL_OPERATOR_LIST + COMMA_OPERATOR


TYPE_COMPARE = {
    str: 3,
    int: 0,
    float: -1,
    dt.date: 2,
    dt.datetime: 1,
    list: 100
}


def get_right_type(left, right):
    tp_left = type(left)
    tp_right = type(right)
    if tp_right in (list, tuple):
        if len(tp_right) > 0:
            tp_right = type(right[0])
        else:
            tp_right = list
    if tp_left == tp_right:
        return tp_left
    if dt.datetime in (tp_right, tp_left):
        return dt.to_datetime
    if dt.date in (tp_right, tp_left):
        return dt.to_date
    rn_tp_left = TYPE_COMPARE[tp_left]
    rn_tp_right = TYPE_COMPARE[tp_right]
    if rn_tp_left == rn_tp_right:
        return tp_left
    elif rn_tp_left < rn_tp_right:
        return tp_left
    else:
        return tp_right


class Expression:
    def __init__(self, left, operator, right=None):
        self.left = left
        self.operator = operator.lower()
        self.right = right

    def evaluate(self):
        pass

    def reset(self, map):
        if isinstance(self.left, Expression):
            self.left.reset(map)
        elif self.left in map:
            self.left = map[self.left]
        if isinstance(self.right, Expression):
            self.right.reset(map)
        elif self.right in map:
            self.right = map[self.right]


class ArithmeticExpr(Expression):
    def __init__(self, left, operator, right=None):
        super().__init__(left, operator, right)
        if operator.lower() not in ARITHMETIC_OPERATOR_LIST:
            raise er.UtilityException('LogicExpr', 'incorrect operator: ', operator)

    def evaluate(self):
        if isinstance(self.left, Expression):
            self.left.evaluate()
        if isinstance(self.right, Expression):
            self.right.evaluate()
        type_ = get_right_type(self.left, self.right)
        self.left = type_(self.left)
        self.right = type_(self.right)
        func = op.get_function(self.operator)
        return func(self.left, self.right)


class LogicExpr(Expression):
    def __init__ (self, left, operator, right=None):
        super().__init__(left, operator, right)
        if operator.lower() not in LOGIC_OPERATOR_LIST:
            raise er.UtilityException('LogicExpr', 'incorrect operator: ', operator)

    def evaluate(self):
        if isinstance(self.left, Expression):
            self.left = self.left.evaluate()
        if isinstance(self.right, Expression):
            self.right = self.right.evaluate()
        if self.operator in op.UNARY_OPERATIONS:
            func = op.get_function(self.operator)
            return func(self.left)
        elif self.operator in ('and', 'or'):
            if type(self.left) != bool or type(self.right) != bool:
                raise er.UtilityException('LogicExpr', 'evaluation', 'logic comparing non-bool values: {0}, {1}')
            func = op.get_function(self.operator)
            return func(self.left, self.right)
        elif type(self.left) != type(self.right):
            type_ = get_right_type(self.left, self.right)
            try:
                self.left = type_(self.left)
                if type(self.right) in (tuple, list):
                    self.right = list(type_(each) for each in self.right)
                else:
                    self.right = type_(self.right)
            except Exception as exc:
                raise er.UtilityException('LogicExpr', 'evaluation', 'can\'t compare {0] and {1}'.format(
                    self.left, self.right
                ), exc)
            func = op.get_function(self.operator)
            return func(self.left, self.right)


def get_expr_type(operator):
    if operator in LOGIC_OPERATOR_LIST:
        return LogicExpr
    elif operator in ARITHMETIC_OPERATOR_LIST:
        return ArithmeticExpr