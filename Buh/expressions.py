import dates as dt
import operations as op
import utility as ut
import smartSplit as ss
import listOperations as lo


class ExpressionError(ut.BaseError):
    pass


DELIMITER_DEFAULT_LIST = ' \t\n'
COMPARE_OPERATOR_LIST = ('<', '>', '=', '<=', '>=', '<>', 'in', 'not in', 'like', 'is none', 'is not none')
BOOL_OPERATOR_LIST = ('and', 'or', 'not')
LOGIC_OPERATOR_LIST = COMPARE_OPERATOR_LIST + BOOL_OPERATOR_LIST
ARITHMETIC_OPERATOR_LIST = ('+', '-', '*', '/', '**')
CONTROL_OPERATOR_LIST = ('(', ')')
COMMA_OPERATOR = (',',)
EVAL_WITH_DIC_ONLY_OPER = ('is none', 'is not none')
OPERATOR_LIST = LOGIC_OPERATOR_LIST + ARITHMETIC_OPERATOR_LIST + CONTROL_OPERATOR_LIST + COMMA_OPERATOR
UNARY_EXPRESSION = 'un'
BINARY_EXPRESSION = 'bin'
COMPLEX_EXPRESSION = 'cmpl'
BOOLEAN_OPERATION = 'bool'
COMPARING_OPERATION = 'cmpr'


TYPE_COMPARE = {
    bool: -50,
    str: 3,
    int: 0,
    float: -1,
    dt.date: 2,
    dt.datetime: 1,
    list: 100,
    type(None): -100
}


EXPRESSION_PRIORITY = {
    1: ['**'],
    2: ['*', '/'],
    3: ['+', '-'],
    4: ['=', '<=', '>=', '<', '>', '<>', 'is none', 'is not none', 'in', 'not in', 'like'],
    5: ['not'],
    6: ['and'],
    7: ['or']
}


def get_right_type(left, right):
    tp_left = type(left)
    tp_right = type(right)
    if tp_right in (list, tuple):
        if len(right) > 0:
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
    def __init__(self, operator, val1, val2=None):
        self.operator = operator.lower()
        self.dictionary = dict()
        if self.operator in op.UNARY_OPERATIONS:
            self.type_ = UNARY_EXPRESSION
            self.variable = val1
        else:
            self.type_ = BINARY_EXPRESSION
            self.left = val1
            self.right = val2

    @classmethod
    def _get_val(cls, var):
        if isinstance(var, cls):
            return var.evaluate()
        return var

    def get_val(self, var):
        val = self._get_val(var)
        if type(val) in (list, tuple): #дописать!!!
            res = list()
            for each in val:
                if each in self.dictionary:
                    res.append(self.dictionary[each])
                else:
                    res.append(each)
            val = tuple(res)
        elif val in self.dictionary:
            return self.dictionary[val]
        return val

    def _un_eval(self):
        pass

    def _bin_eval(self):
        pass

    def __evaluate__(self):
        if self.type_ == UNARY_EXPRESSION:
            return self._un_eval()
        elif self.type_ == BINARY_EXPRESSION:
            return self._bin_eval()

    def evaluate(self):
        return self.__evaluate__()

    def _un_reset(self, map):
        if isinstance(self.variable, Expression):
            self.variable.__reset__(map)
        self.dictionary = map

    def _bin_reset(self, map):
        if isinstance(self.right, Expression):
            self.right.__reset__(map)
        if isinstance(self.left, Expression):
            self.left.__reset__(map)
        self.dictionary = map

    def __reset__(self, map):
        if self.type_ == UNARY_EXPRESSION:
            self._un_reset(map)
        else:
            self._bin_reset(map)

    def reset(self, map):
        if type(map) != dict:
            raise ExpressionError('Error while set expression map: only dictionary allowed (get {})'.format(map))
        self.__reset__(map)


class ArithmeticExpr(Expression):
    def __init__(self, operator, val1, val2=None):
        super().__init__(operator, val1, val2)
        if operator.lower() not in ARITHMETIC_OPERATOR_LIST:
            raise ExpressionError('LogicExpr', 'incorrect operator', operator)

    def _bin_eval(self):
        left = self.get_val(self.left)
        right = self.get_val(self.right)
        if type(left) != type(right):
            type_ = get_right_type(left, right)
            if type_ == type(None):
                return None
            left = type_(left)
            right = type_(right)
        func = op.get_function(self.operator)
        return func(left, right)

    def _un_eval(self):
        if self.operator in EVAL_WITH_DIC_ONLY_OPER and not self.dictionary \
                and not isinstance(self.variable, Expression) and type(self.variable) == str:
            raise ExpressionError('Can\'t resolve {0} operator without it\'s operand!')
        var = self.get_val(self.variable)
        func = op.get_function(self.operator)
        return func(var)


class LogicExpr(Expression):
    def __init__ (self, operator, val1, val2=None):
        super().__init__(operator, val1, val2)
        if operator.lower() not in LOGIC_OPERATOR_LIST:
            raise ExpressionError('LogicExpr', 'incorrect operator', operator)
        if operator in BOOL_OPERATOR_LIST:
            self.operation_type = BOOLEAN_OPERATION
        else:
            self.operation_type = COMPARING_OPERATION

    def _un_eval(self):
        if self.operator in EVAL_WITH_DIC_ONLY_OPER and not self.dictionary \
                and not isinstance(self.variable, Expression) and type(self.variable) == str:
            raise ExpressionError('Can\'t resolve {0} operator without it\'s operand!'.format(self.operator))
        var = self.get_val(self.variable)
        func = op.get_function(self.operator)
        return func(var)

    def _bin_eval(self):
        left = self.get_val(self.left)
        right = self.get_val(self.right)
        if type(left) != type(right):
            type_ = get_right_type(left, right)
            if type_ == type(None):
                return None
            try:
                left = type_(left)
                if type(right) in (tuple, list):
                    right = list(type_(each) for each in right)
                else:
                    right = type_(right)
            except Exception as exc:
                raise ExpressionError('LogicExpr', 'evaluation', 'can\'t compare {0} and {1}'.format(
                    left, right
                ), exc)
        func = op.get_function(self.operator)
        return func(left, right)


def get_expr_type(operator):
    if operator in LOGIC_OPERATOR_LIST:
        return LogicExpr
    elif operator in ARITHMETIC_OPERATOR_LIST:
        return ArithmeticExpr


class ExpressionParser:
    def __init__(self, str_):
        self.str_ = str_.lower()

    def reset_str(self, str_):
        self.str_ = str_.lower()

    @staticmethod
    def _parse_simple_list(lst_):
        ls = lst_
        for num in range(1, len(EXPRESSION_PRIORITY) + 1):
            i = lo.find_obj(ls, EXPRESSION_PRIORITY[num], list_obj=True)
            while i != -1:
                elem = ls[i]
                expr_type = get_expr_type(elem)
                if elem in op.UNARY_PRE_OPERATIONS:
                    val1_i = i - 1
                    val2_i = None
                elif elem in op.UNARY_POST_OPERATIONS:
                    val1_i = i + 1
                    val2_i = None
                else:
                    val1_i = i - 1
                    val2_i = i + 1
                val1 = ls[val1_i]
                if val2_i is not None:
                    val2 = ls[val2_i]
                else:
                    val2 = val2_i
                expr = expr_type(elem, val1, val2)
                if elem not in EVAL_WITH_DIC_ONLY_OPER:
                    try:
                        expr = expr.evaluate()
                    except ExpressionError:
                        pass
                if val1_i < i and val2_i is None:
                    val2_i = i
                elif val2_i is None:
                    val2_i = val1_i
                    val1_i = i
                ls = lo.replace_sublist(ls, val1_i, val2_i, expr)
                i = lo.find_obj(ls, EXPRESSION_PRIORITY[num], list_obj=True)
        return ls

    def parse_list(self, lst_):
        ls = lst_
        coordinates = lo.get_sublist(ls, '(', ')')
        while coordinates is not None:
            tmp = self._parse_simple_list(ls[coordinates[0] + 1: coordinates[1]])
            ls = lo.replace_sublist(ls, coordinates[0], coordinates[1], *tmp)
            coordinates = lo.get_sublist(ls, '(', ')')
        ls = self._parse_simple_list(ls)
        return ls[0]

    def parse(self, str_=None):
        if str_ is None:
            str_ = self.str_
        splitted_str = ss.smart_split(str_, OPERATOR_LIST, DELIMITER_DEFAULT_LIST)
        expr = self.parse_list(splitted_str)
        return expr




if __name__ == '__main__':
    a = None
    b = 'field'
    c = LogicExpr('and', a, b)
    dic = {'field': True}
    c.reset(dic)
    print(c.evaluate())
    print(c.left, c.get_val(c.right))
    str_ = "1 = 0 and 1 not in ('', 0) or ('2018-01-01' < '2018-01-02') and none is none"
    print(ss.smart_split(str_, OPERATOR_LIST, ' \t\n'))
    a = ExpressionParser(str_)
    c = a.parse()
    dic = {'': 1, 'none': None}
    c.reset(dic)
    print(c.operator, c.left, c.right)
    print(c.evaluate())
    print(c.left.operator, c.left.left, c.left.right)
    # print(c.evaluate())
    # print(c.right, c.left, c.operator)
    # print(c.left.left, c.left.right, c.left.operator)
    # print(c.left.right.left, c.left.right.right, c.left.right.operator)
    str_ = "sdf < 1"
    a.reset_str(str_)
    c = a.parse()
    print(c)
    c.reset({'sdf': 0})
    print(c.evaluate())

