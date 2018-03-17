"""
вся работа с датами
"""
from datetime import date
from datetime import datetime
import datetime as dt


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
        str_ = datetime.now().strftime(refmt(fmt))
    return datetime.strptime(str_, refmt(fmt))


def str_to_date(str_, fmt=DATE_DEFAULT_FMT):
    if type(str_) == str and str_ == ACTUALITY_DATE_VALUE:  # проставляем current_date
        str_ = datetime.now().strftime(refmt(fmt))
    return datetime.strptime(str_, refmt(fmt)).date()


def datetime_to_str(date_, fmt=DATETIME_DEFAULT_FMT):
    if type(date_) == str and date_ == ACTUALITY_DTTM_VALUE:  # проставляем current_timestamp
        date_ = datetime.now()
    elif type(date_) == str:
        date_ = str_to_datetime(date_)
    if type(date_) not in (datetime, dt.datetime):
        raise ValueError('Error conversion {0} to str: wrong type({1})'.format(str(date_), type(date_)))
    return datetime.strftime(date_, refmt(fmt))


def date_to_str(date_, fmt=DATE_DEFAULT_FMT):
    if type(date_) == str and date_ == ACTUALITY_DATE_VALUE:  # проставляем current_date
        date_ = datetime.now().date()
    elif type(date_) == str:
        date_ = str_to_date(date_)
    if type(date_) not in (date, dt.date):
        raise ValueError('Error conversion {0} to str: wrong type({1})'.format(str(date_), type(date_)))
    return date.strftime(date_, refmt(fmt))


def to_date(date, fmt=DATE_DEFAULT_FMT):        # прифведение кастомного типа к дате
    if type(date) == str:
        return str_to_date(date, fmt)
    elif type(date) in (date, dt.date):
        return date
    elif type(date) in (datetime, dt.datetime):
        return date.date()
    else:
        raise ValueError('Transformation from {0} to date does not supported'.format(type(date)))


def to_datetime(date, fmt=DATETIME_DEFAULT_FMT):        # приведение кастомного типа к датевремени
    if type(date) == str:
        return str_to_datetime(date, fmt)
    elif type(date) in (date, dt.date):
        return datetime(date.year, date.month, date.day)
    elif type(date) in (datetime, dt.datetime):
        return date
    else:
        raise ValueError('Transformation from {0} to date does not supported'.format(type(date)))


MONTH_DAYS_RANGE = {
    1: range(1,32),
    2: range(1,30),
    3: range(1,32),
    4: range(1,31),
    5: range(1,32),
    6: range(1,31),
    7: range(1,32),
    8: range(1,32),
    9: range(1,31),
    10:range(1,32),
    11:range(1,31),
    12:range(1,32)
}


def decode_datepiece(data, fmt):
    year = fmt.find('YYYY')
    if year != -1:
        year = int(data[year : year + 4])
    else:
        smallyear = fmt.find('YY')
        if smallyear == -1:
            raise ValueError('Incorrect datepiece format: year not found ({})'.format(fmt))
        year = 2000 + int(data[smallyear : smallyear + 2])
    month = fmt.find('MM')
    if month != -1:
        month = int(data[month : month + 2])
    else:
        month = range(1,13)
    day = fmt.find('DD')
    if day != -1:
        if isinstance(month, list):
            raise ValueError('Incorrect datepiece format: year not found ({})'.format(fmt))
        day = int(data[day : day + 2])
    else:
        if isinstance(month, range):
            day = range(1,32)
        else:
            day = MONTH_DAYS_RANGE[month]
    return year, month, day


class dateRange():
    """Специальный класс для обработки логики вхождения дат в диапазоны (неподдерживает сравнения двух диапазонов
    не поддерживает сравнения двух дат).

    super - переменная, указывающая на то что объект содержит дату, а не диапазон
    инициализируется датой, датой-временеам, строкой и форматом, тремя кастомными значениями

    Реализован исключительно для обработки логики фильтрации партиций для ModelFile.py"""

    class StopRange(BaseException):
        pass

    class NoneTypeError(BaseException):
        pass

    def __init__(self, data=None, fmt=None, year=None, month=None, day=None):
        if type(data) in (date, dt.date, datetime, dt.datetime):
            self.super = True
            self.year = data.year
            self.month = data.month
            self.day = data.day
        elif isinstance(data, str):
            self.super = False
            if fmt is None:
                raise BaseException('Error datePiece init: got data type = \'{0}\' ({1}) and it\'s format: {2}'.format(
                    type(data), str(data), fmt
                ))
            self.year, self.month, self.day = decode_datepiece(data, fmt)
            if isinstance(self.day, int):
                raise self.StopRange()
        elif year is not None:
            self.super = False
            self.year = year
            if type(year) == range:
                self.month = range(1,13)
                self.day = range(1,32)
            elif type(year) == int:
                if month is not None:
                    self.month = month
                    if type(month) == range:
                        self.day = range(1,32)
                    elif type(month) == int:
                        if day is not None:
                            self.day = day
                            if isinstance(day, int):
                                self.super = True
                            if type(day) not in (int, range):
                                raise TypeError('Incorrect type for day: {}'.format(type(day)))
                        else:
                            self.day = MONTH_DAYS_RANGE[self.month]
                    else:
                        raise TypeError('Incorrect type for month: {}'.format(type(month)))
                else:
                    self.month = range(1,13)
                    self.day = range(1,32)
            else:
                raise TypeError('Incorrect type for year: {}'.format(type(year)))
        else:
            raise self.NoneTypeError()

    def _is_super(self):
        return self.super

    def _check_types(self, other):
        if (self.super == other._is_super()):
            raise ValueError('Can\'t compare two date ranges')

    def in_range(self, other, shift = 0):
        if not (other.year == self.year or isinstance(self.year, range) and other.year in self.year):
            return False
        if not (other.month == self.month or isinstance(self.month, range) and other.month in self.month):
            return False
        elif isinstance(self.month, range) and other.month in self.month:
            return True
        if other.day + shift not in self.day:
            return False
        return True

    def other_less_then_floor(self, other):
        if isinstance(self.year, range):
            return self.year.start > other.year
        if self.year > other.year:
            return True
        elif self.year < other.year:
            return False
        if isinstance(self.month, range):
            return self.month.start > other.month
        if self.month > other.month:
            return True
        elif self.month < other.month:
            return False
        return self.day.start > other.day

    def other_greater_then_ceil(self, other):
        if isinstance(self.year, range):
            return self.year.stop - 1 < other.year
        if self.year < other.year:
            return True
        elif self.year > other.year:
            return False
        if isinstance(self.month, range):
            return self.month.stop - 1 < other.month
        if self.month < other.month:
            return True
        elif self.month > other.month:
            return False
        return self.day.stop - 1 < other.day

    def __eq__(self, other):
        self._check_types(other)
        if self.super:
            return other.in_range(self)
        else:
            return self.in_range(other)

    def __ne__(self, other):
        self._check_types(other)
        return True

    def __ge__(self, other):
        self._check_types(other)
        if self.super:
            return other <= self
        else:
            if self.in_range(other):
                return True
            return self.other_less_then_floor(other)

    def __le__(self, other):
        self._check_types(other)
        if self.super:
            return other >= self
        else:
            if self.in_range(other):
                return True
            return self.other_greater_then_ceil(other)

    def __gt__(self, other):
        self._check_types(other)
        if self.super:
            return other < self
        else:
            if self.in_range(other, 1):
                return True
            return self.other_less_then_floor(other)

    def __lt__(self, other):
        self._check_types(other)
        if self.super:
            return other > self
        else:
            if self.in_range(other, -1):
                return True
            return self.other_greater_then_ceil(other)

    def __str__(self):
        return str(self.year) + '-' + str(self.month) + '-' + str(self.day)


def to_dateRange(data):
    if isinstance(data, dateRange):
        return data
    if data is None:
        return None
    else:
        return dateRange(data)


if __name__ == '__main__':
    b = dateRange('20181201', 'YYYYMMDD')
    a = dateRange(date(2018,11,30))
    c = dateRange(date(2017,12,31))
    d = (c, b)
    print('a = ', a)
    print('b = ', b)
    print(a > b, a < b, a == b, a != b, a <= b, a >= b)