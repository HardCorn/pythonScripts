import modelExceptions as er
import datetime as dt
import operations


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
    elif type(date) == str:
        date = str_to_datetime(date)
    if type(date) != dt.datetime:
        raise er.UtilityException('Error conversion {0} to str: wrong type({1})'.format(str(date), type(date)))
    return dt.datetime.strftime(date, refmt(fmt))


def date_to_str(date, fmt=DATE_DEFAULT_FMT):
    if type(date) == str and date == ACTUALITY_DATE_VALUE:  # проставляем current_date
        date = dt.datetime.now().date()
    elif type(date) == str:
        date = str_to_date(date)
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


def str_to_type(str_):
    if str_.isnumeric():
        return int(str_)
    if str_.count('.') == 1 and str_.replace('.', '').isnumeric():
        return float(str_)
    try:
        return str_to_date(str_.strip('\''))
    except Exception:
        pass
    try:
        return str_to_datetime(str_.strip('\''))
    except Exception:
        pass
    return str_


def get_min_delimiter(str_, split_list=' ()\t\n,'):
    tmp = list()
    for each in (split_list):
        tmp2 = str_.find(each)
        if tmp2 != -1:
            tmp.append(tmp2)
    tmp.sort()
    if len(tmp) > 0:
        return tmp[0]
    else:
        return -1


def smart_split(str_, split_list=' ()\t\n,'):
    res = list()
    tmp_list = list()
    buffer = str_.lower().replace('\'\'', '"')
    tmp_word = ''
    delim = get_min_delimiter(buffer, split_list)
    while delim != -1:
        tmp = buffer[:delim]
        delimiter = buffer[delim]
        buffer = buffer[delim + 1:]
        qt_start = tmp.find("'")
        if tmp in ('and', 'or'):
            res.append(tmp)
        elif tmp in ('<', '>', '<=', '>=', '=', '<>', 'like', '+', '-', '*', '/', '**'):
            res.append(tmp)
        elif tmp in ('not', 'is'):
            if tmp_word == 'is' and tmp == 'not':
                tmp_word += ' ' + tmp
            else:
                if tmp_word != '':
                    res.append(tmp_word)
                tmp_word = tmp
        elif tmp == 'in':
            if tmp_word == 'not':
                res.append(tmp_word + ' ' + tmp)
            else:
                res.append(tmp)
            tmp_word = ''
        elif tmp == 'none':
            res.append(tmp_word + ' ' + tmp)
            tmp_word = ''
        elif tmp_word == 'not':
            if tmp_word != '':
                res.append(tmp_word)
            tmp_word = tmp
        elif qt_start != -1:
            tmp_word += tmp[:qt_start]
            qt_end = tmp[qt_start + 1:].find("'")
            bf_qt = buffer.find("'")
            if tmp_word != '':
                res.append(tmp_word)
            if qt_end != -1:
                res.append(str_to_type(tmp[qt_start:qt_end + 3].replace('"', '\'\'')))
                buffer = tmp[qt_end + 3:] + buffer
            elif bf_qt != -1:
                res.append(str_to_type(tmp[qt_start:] + buffer[:bf_qt + 3].replace('"', '\'\'')))
                buffer = buffer[bf_qt + 3:]
            else:
                raise er.UtilityException('Smart split error: unclosed quotation mark')
            tmp_word = ''
        else:
            if delimiter != ',' and tmp != '':
                res.append(str_to_type(tmp))
        if delimiter in ('(', ',', ')'):
            res.append(delimiter)
        delim = get_min_delimiter(buffer)
    if buffer != '':
        res.append(str_to_type(buffer))
    return res


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
        if operator.lower() not in ('+', '-', '*', '/', '**'):
            raise er.UtilityException('LogicExpr', 'incorrect operator: ', operator)

    def evaluate(self):
        if isinstance(self.left, Expression):
            self.left.evaluate()
        if isinstance(self.right, Expression):
            self.right.evaluate()
        type_ = get_right_type(self.left, self.right)
        self.left = type_(self.left)
        self.right = type_(self.right)
        func = operations.get_function(self.operator)
        return func(self.left, self.right)


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
            func = operations.get_function(self.operator)
            return func(self.left)
        elif self.operator in ('and', 'or'):
            if type(self.left) != bool or type(self.right) != bool:
                raise er.UtilityException('LogicExpr', 'evaluation', 'logic comparing non-bool values: {0}, {1}')
            func = operations.get_function(self.operator)
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
            func = operations.get_function(self.operator)
            return func(self.left, self.right)


def get_expr_type(operator):
    if operator in ('<', '>', '=', '<=', '>=', '<>', 'in', 'not in', 'like', 'and', 'or', 'not', 'is none', 'is not none'):
        return LogicExpr
    elif operator in ('+', '-', '*', '/', '**'):
        return ArithmeticExpr


class ExpressionParser:
    def __init__(self, str_):
        self.str_ = str_

    def parse_input(self):
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
    str = "1 = 0 and 1 not in '2' or ('2018-01-01' < '2018-01-02') and self_name is none ('22', '33', '44')"
    print(str)
    print(smart_split(str))
