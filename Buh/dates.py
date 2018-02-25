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
    if type(date_) != datetime:
        raise ValueError('Error conversion {0} to str: wrong type({1})'.format(str(date_), type(date_)))
    return datetime.strftime(date_, refmt(fmt))


def date_to_str(date_, fmt=DATE_DEFAULT_FMT):
    if type(date_) == str and date_ == ACTUALITY_DATE_VALUE:  # проставляем current_date
        date_ = datetime.now().date()
    elif type(date_) == str:
        date_ = str_to_date(date_)
    if type(date_) != date_:
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