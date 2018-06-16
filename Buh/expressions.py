"""Модуль описывающий работу кастомных выражений"""
import dates as dt
import operations as op
import utility as ut
import smartSplit as ss
from smartSplit import UnConvString as Operand
import listOperations as lo


class ExpressionError(ut.BaseError):
    pass


# # # КОНСТАНТЫ # # #
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
    str: 4,
    int: 0,
    float: -1,
    dt.date: 3,
    dt.datetime: 2,
    dt.dateRange: 1,
    list: 100,
    type(None): -100
}   # словарь для приоретизации типов данных


EXPRESSION_PRIORITY = {
    1: ['**'],
    2: ['*', '/'],
    3: ['+', '-'],
    4: ['=', '<=', '>=', '<', '>', '<>', 'is none', 'is not none', 'in', 'not in', 'like'],
    5: ['not'],
    6: ['and'],
    7: ['or']
}   # словарь приоретизации операторов


def get_right_type(left, right):    # функция выбираем тип с высшим приоритетом (для кастомного приведения
    tp_left = type(left)
    tp_right = type(right)
    if tp_right in (list, tuple):   # если получили список смотрим тип его первого элемента, подразумевая что данные там типизированы
        if len(right) > 0:
            tp_right = type(right[0])
        else:
            tp_right = list         # если список пустой - ставим типом список
    if tp_left == tp_right:
        return tp_left
    if type(None) in (tp_left, tp_right):
        return type(None)
    if dt.dateRange in (tp_left, tp_right):
        return dt.to_dateRange
    if dt.datetime in (tp_right, tp_left):  # если получили дату\датувремя - вместо типов возвращаем функции приведения к ним
        return dt.to_datetime
    if dt.date in (tp_right, tp_left):
        return dt.to_date
    rn_tp_left = TYPE_COMPARE[tp_left]      # забираем из словаря ранги типов и выбираем нужный с минимальным рангом)
    rn_tp_right = TYPE_COMPARE[tp_right]
    if rn_tp_left == rn_tp_right:
        return tp_left
    elif rn_tp_left < rn_tp_right:
        return tp_left
    else:
        return tp_right


class Expression:
    """
        Базовый класс для описания выражений:
        инициализируется оператором и списком операндов:
        для бинарных выражений операнды в инициализации указываем в порядке: левый, правый
        класс формальный
    """
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

    def _bin_to_str(self):
        if isinstance(self.left, Expression):
            str_left = '(' + self.left.__str__() + ')'
        else:
            str_left = str(self.left)
        if isinstance(self.right, Expression):
            str_right = '(' + self.right.__str__() + ')'
        else:
            str_right = str(self.right)
        return str_left + ' ' + self.operator + ' ' + str_right

    def _un_to_str(self):
        if isinstance(self.variable, Expression):
            var_str = '(' + self.variable.__str__() + ')'
        else:
            var_str = str(self.variable)
        if self.operator in op.UNARY_PRE_OPERATIONS:
            return var_str + ' ' + self.operator
        else:
            return self.operator + ' ' + var_str

    def __str__(self):
        if self.operator in op.UNARY_OPERATIONS:
            return self._un_to_str()
        else:
            return self._bin_to_str()

    @classmethod
    def _get_val(cls, var): # функция для получения операндов: если это другое выражение - возвращаем его результат
        if isinstance(var, cls):
            return var.evaluate()
        return var

    def get_val(self, var): # функция расширяет предыдущую проверяя в словаре наличие полученного операнда и подменяет его при обнаружении
        val = self._get_val(var)
        if type(val) in (list, tuple): # отдельно обрабатываем операнды списков
            res = list()
            for each in val:
                if isinstance(each, Operand):
                    try:
                        res.append(self.dictionary[each])
                    except KeyError:
                        raise ExpressionError('Operand \'{0}\' not found in the dictionary \'{1}\''.format(
                            each, self.dictionary
                        ))
                elif isinstance(each, ss.SmartSplitString):
                    res.append(str(each))
                else:
                    res.append(each)
            val = tuple(res)
        elif isinstance(val, Operand):
            try:
                return self.dictionary[val]
            except KeyError:
                raise ExpressionError('Operand \'{0}\' not found in the dictionary \'{1}\''.format(
                    val, self.dictionary
                ))
        elif isinstance(val, ss.SmartSplitString):
            val = str(val)
        return val

    def _un_eval(self):
        pass    # базовая функцию вычисления унарного выражения - описывается в детях класса

    def _bin_eval(self):
        pass    # базовая функция вычисления бинарного выражения - описывается в детях класса

    def __evaluate__(self): # функция, определяющая тип выражения и в зависимости от него вызывающая нужную базовую
        if self.type_ == UNARY_EXPRESSION:
            return self._un_eval()
        elif self.type_ == BINARY_EXPRESSION:
            return self._bin_eval()

    def evaluate(self): # обертка, возвращающая результат вычислений
        return self.__evaluate__()

    def _un_reset(self, map):   # базовая функция для подмены словаря унарного выражения
        if isinstance(self.variable, Expression):
            self.variable.__reset__(map)
        self.dictionary = map

    def _bin_reset(self, map):  # базовая функция для подмены словаря бинарного выражения
        if isinstance(self.right, Expression):
            self.right.__reset__(map)
        if isinstance(self.left, Expression):
            self.left.__reset__(map)
        self.dictionary = map

    def __reset__(self, map):   # функция определяет тип выражения и вызывает нужную базовую функцию
        if self.type_ == UNARY_EXPRESSION:
            self._un_reset(map)
        else:
            self._bin_reset(map)

    def reset(self, map_):  # обертка, дополнительно проверяет что на вход получен именно словарь
        if type(map_) != dict:
            raise ExpressionError('Error while set expression map: only dictionary allowed (get {})'.format(map))
        self.__reset__(map_)


class ArithmeticExpr(Expression):   # класс, описывающий арифметические выражения
    def __init__(self, operator, val1, val2=None):
        super().__init__(operator, val1, val2)
        if operator.lower() not in ARITHMETIC_OPERATOR_LIST:    # проверяем что оператор действительно арифметический
            raise ExpressionError('LogicExpr', 'incorrect operator', operator)

    def _bin_eval(self):
        left = self.get_val(self.left)  # получаем операнды
        right = self.get_val(self.right)
        if type(left) != type(right):   # сравниваем их типы
            type_ = get_right_type(left, right)
            if type_ == type(None):     # если получили None - сразу его возвращаем
                return None
            left = type_(left)          # приводим типы (без обработки, если что-то некорректно - пусть падает)
            right = type_(right)
        func = op.get_function(self.operator)   # получаем функцию для расчета выражения
        return func(left, right)

    def _un_eval(self):
        var = self.get_val(self.variable)
        func = op.get_function(self.operator)
        return func(var)


class LogicExpr(Expression):    # класс для описания логических выражений
    def __init__ (self, operator, val1, val2=None):
        super().__init__(operator, val1, val2)
        if operator.lower() not in LOGIC_OPERATOR_LIST:
            raise ExpressionError('LogicExpr', 'incorrect operator', operator)
        if operator in BOOL_OPERATOR_LIST:  # дополнительно выявляем булевые операции и операции сравнения
            self.operation_type = BOOLEAN_OPERATION
        else:
            self.operation_type = COMPARING_OPERATION

    def _un_eval(self):
        var = self.get_val(self.variable)
        func = op.get_function(self.operator)   # функция для NOT сама проверяет тип операнда
        return func(var)

    def _bin_eval(self):    # расчет бинарных выражений
        left = self.get_val(self.left)
        if (self.operator == 'and' and left is False) or (self.operator == 'or' and left is True):
            return left
        right = self.get_val(self.right)
        if type(left) != type(right):
            type_ = get_right_type(left, right)
            if type(None) == type_:     # сравниваем типы, если получили None - возвращаем False
                return False
            try:
                left = type_(left)
                if type(right) in (tuple, list):    # здесь дополнительно обрабатываем правые операнды-списки
                    right = list(type_(each) for each in right)
                else:
                    right = type_(right)
            except Exception:
                raise ExpressionError('LogicExpr', 'evaluation', 'can\'t compare {0} and {1}'.format(left, right))
        func = op.get_function(self.operator)
        if isinstance(left, str):
            left = left.lower()
        if isinstance(right, str):
            right = right.lower()
        return func(left, right)


def get_expr_type(operator):    # функция, возвращает нужный тип выражения
    if operator in LOGIC_OPERATOR_LIST:
        return LogicExpr
    elif operator in ARITHMETIC_OPERATOR_LIST:
        return ArithmeticExpr


class ExpressionParser(ut.SingleTon):
    """
        Класс, основная функция которого - парсить строковые выражения и возвращать либо объект Expression, либо результат
        Кэширует предыдущие результаты
    """

    def _init(self):
        self.data = dict()

    @staticmethod
    def _parse_simple_list(lst_):   # функция, возвращает результат разбора простой строки (без скобочек)
        ls = lst_
        for num in range(1, len(EXPRESSION_PRIORITY) + 1):  # Пробегаемся по приоритетам операций
            i = lo.find_obj(ls, EXPRESSION_PRIORITY[num], list_obj=True)    # ищем первое вхождение любой из операций с данным приоритетом
            while i != -1:
                elem = ls[i]                                # сохраняем элемент списка
                expr_type = get_expr_type(elem)             # получаем тип операции
                if elem in op.UNARY_PRE_OPERATIONS:         # забираем индексы операндов
                    val1_i = i - 1
                    val2_i = None
                elif elem in op.UNARY_POST_OPERATIONS:
                    val1_i = i + 1
                    val2_i = None
                else:
                    val1_i = i - 1
                    val2_i = i + 1
                val1 = ls[val1_i]                           # собираем по индексам операнды
                if val2_i is not None:
                    val2 = ls[val2_i]
                else:
                    val2 = val2_i
                expr = expr_type(elem, val1, val2)          # объявляем выражение
                try:
                    expr = expr.evaluate()
                except ExpressionError:
                    pass
                if val1_i < i and val2_i is None:           # получаем индексы обработанных элеметов списка для замены на выражение
                    val2_i = i
                elif val2_i is None:
                    val2_i = val1_i
                    val1_i = i
                ls = lo.replace_sublist(ls, val1_i, val2_i, expr)   # подменяем их на выражение
                i = lo.find_obj(ls, EXPRESSION_PRIORITY[num], list_obj=True)    # повторяем поиск
        return ls

    def parse_list(self, lst_):
        ls = lst_
        coordinates = lo.get_sublist(ls, '(', ')')  # получаем координаты простого подмассива
        while coordinates is not None:
            tmp = self._parse_simple_list(ls[coordinates[0] + 1: coordinates[1]])   # парсим его
            ls = lo.replace_sublist(ls, coordinates[0], coordinates[1], *tmp)       # заменяем
            coordinates = lo.get_sublist(ls, '(', ')')                              # ищем следующий
        ls = self._parse_simple_list(ls)                                            # когда их не осталось - разбираем остатки
        return ls[0]

    def parse(self, str_): # функция-парсер строки
        if type(str_) != str:
            raise ExpressionError('Parsing string', "can't parse this type ({}) only str allowed!".format(type(str_)))
        if not str_:
            raise ExpressionError('Parsing string', "can't parse empty string!")
        # str_ = str_.lower() # если получили приводим к low-case
        self.str_ = str_
        if str_ in self.data: # проверяем не смотрели ли мы уже такую строку
            return self.data[str_]
        splitted_str = ss.smart_split(str_, OPERATOR_LIST, DELIMITER_DEFAULT_LIST)  # бьем строку на список
        expr = self.parse_list(splitted_str)                                        # парсим список
        self.data[str_] = expr                                                # сохраняем результат
        return expr


GLOBAL_PARSER = ExpressionParser()


def parse(str_):
    return GLOBAL_PARSER.parse(str_)


if __name__ == '__main__':
    # a = None
    # b = 'field'
    # c = LogicExpr('and', a, b)
    # dic = {'field': True}
    # c.reset(dic)
    # print(c.evaluate())
    # print(c.left, c.get_val(c.right))
    str_ = "1 = 0 and 1 not in ('', 0) or ('2018-01-01' < '2018-01-02') and none is none and 1 not in ('', 0)"
    # test = ss.smart_split(str_, OPERATOR_LIST, DELIMITER_DEFAULT_LIST)
    # for each in test:
    #     print(each, ': ', type(each))
    # print(ss.smart_split(str_, OPERATOR_LIST, ' \t\n'))
    a = ExpressionParser()
    # c = a.parse()
    # dic = {'': 1, 'none': None}
    # c.reset(dic)
    # print(c.operator, c.left, c.right)
    # print(c.evaluate())
    # print(c.left.operator, c.left.left, c.left.right)
    # print(c.evaluate())
    # print(c.right, c.left, c.operator)
    # print(c.left.left, c.left.right, c.left.operator)
    # print(c.left.right.left, c.left.right.right, c.left.right.operator)
    # str_ = "sdf < 1"
    # c = a.parse(str_)
    # d = a.parse(str_)
    # print(c)
    # c.reset({'sdf': 0})
    # str_ =  ' 3 + 2 * 6 ** 2 < 8 ** 4 and not (20 > 5) or field > 2 + 2'
    b = a.parse(str_)
    print(b)
    # print(b.evaluate())
    b.reset({'': 5, 'none': None})
    print(b, b.evaluate(), b)
    # print(c.evaluate(), c)

