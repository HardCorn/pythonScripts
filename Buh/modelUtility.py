import modelExceptions as er
import datetime as dt
import re


DEBUG = False
DATE_DEFAULT_FMT = 'YYYY-MM-DD'                         # формат по-умолчанию для типа дата
DATETIME_DEFAULT_FMT = 'YYYY-MM-DD HH:MI:SS.SSSSSS'      # формат по-умолчанию для типа дата-время
DAILY_PARTITION_FMT = 'YYYYMMDD'                        # формат дат для ежедневных партиций
MONTH_PARTITION_FMT = 'YYYYMM'                          # формат дат для месячных партиций
YEAR_PARTITION_FMT = 'YYYY'                             # формат для годовых партиций
SHORT_YEAR_PARTITION_FMT = 'YY'                         # короткий формат для годовых партиций
ACTUALITY_DTTM_VALUE = 'current_timestamp'              # значение атрибута актуальности - текущие дата-время
ACTUALITY_DATE_VALUE = 'current_date'                   # значение атрибута актуальности - текущая дата


def refmt(fmt):                     # приводим к форматам питона, не предполагаем никаких экстравагантных форматов
    return fmt.upper().replace('YYYY', '%Y').replace('YY', '%y').replace('MM', '%m').replace('DD', '%d').replace(
        'HH', '%H').replace('MI', '%M').replace('SSSSSS', '%f').replace('SS', '%S')


def str_to_datetime(str_, fmt=DATETIME_DEFAULT_FMT):
    if type(str_) == str and str_ == ACTUALITY_DTTM_VALUE:  # проставляем current_timestamp
        str_ = dt.datetime.now().strftime(refmt(fmt))
    return dt.datetime.strptime(str_, refmt(fmt))


def str_to_date(str_, fmt=DATE_DEFAULT_FMT):
    if type(str_) == str and str_ == ACTUALITY_DATE_VALUE:  # проставляем current_date
        str_ = dt.datetime.now().strftime(refmt(fmt))
    return dt.datetime.strptime(str_, refmt(fmt)).date()


def datetime_to_str(date, fmt=DATETIME_DEFAULT_FMT):
    if type(date) == str and date == ACTUALITY_DTTM_VALUE:  # проставляем current_timestamp
        date = dt.datetime.now()
    if type(date) != dt.datetime:
        raise er.UtilityException('Error conversion {0} to str: wrong type({1})'.format(str(date), type(date)))
    return dt.datetime.strftime(date, refmt(fmt))


def date_to_str(date, fmt=DATE_DEFAULT_FMT):
    if type(date) == str and date == ACTUALITY_DATE_VALUE:  # проставляем current_date
        date = dt.datetime.now().date()
    if type(date) != dt.date:
        raise er.UtilityException('Error conversion {0} to str: wrong type({1})'.format(str(date), type(date)))
    return dt.date.strftime(date, refmt(fmt))


TYPE_COMPARE = {
    str: 1,
    int: 0,
    float: -1,
    dt.date: 3,
    dt.datetime: 2,
    'empty_list': 100
}


def get_right_type(left, right):
    tp_left = type(left)
    tp_right = type(right)
    if tp_right in (list, tuple):
        if len(tp_right) > 0:
            tp_right = type(right[0])
        else:
            tp_right = 'empty_list'
    if tp_left == tp_right:
        return tp_left
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


class LogicExpr(Expression):
    def __init__ (self, left, operator, right=None):
        super().__init__(left, operator, right)
        if operator.lower() not in ('<', '>', '=', '<=', '>=', '<>', 'in', 'not in', 'like', 'and', 'or', 'not', 'is none', 'is not none'):
            raise er.UtilityException('LogicExpr', 'incorrect operator: ', operator)

    def evaluate(self):
        if isinstance(self.left, Expression):
            self.left = self.left.evaluate()
        if isinstance(self.right, Expression):
            self.right = self.right.evaluate()
        if self.operator in ('not', 'is none', 'is not none'):
            if self.operator == 'not':
                return not self.left
            elif self.operator == 'is none':
                return self.left is None
            elif self.operator == 'is not none':
                return self. left is not None
        elif self.operator in ('and', 'or'):
            if type(self.left) != bool or type(self.right) != bool:
                raise er.UtilityException('LogicExpr', 'evaluation', 'logic comparing non-bool values: {0}, {1}')
            elif self.operator == 'or':
                return self.left or self.right
            elif self.operator == 'and':
                return self.left and self.right
        elif self.operator == 'like':
            pass
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
            if self.operator == '>':
                return self.left > self.right
            elif self.operator == '<':
                return self.left < self.right
            elif self.operator == '=':
                return self.left == self.right
            elif self.operator == '<=':
                return self.left <= self.right
            elif self.operator == '>=':
                return self.left >= self.right
            elif self.operator == '<>':
                return self.left != self.right
            elif self.operator == 'in':
                return self.left in self.right
            elif self.operator == 'not in':
                return self.left not in self.right
            elif self.operator == 'like':
                if


class ExpressionParser:
    pass


class Filter:
    def __init__(self, logic_clause):
        self.data = self.parse(logic_clause)

    def parse(self, logic_clause):
        res_dict = dict()

        return res_dict

    def logic_refactor(self, logic_clause):
        pass


if __name__ == '__main__':
    a = LogicExpr(2, '>', '3')
    print(isinstance(a, Expression))