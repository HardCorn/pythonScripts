import datetime as dt


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
        raise BaseException('Error conversion {0} to str: wrong type({1})'.format(str(date), type(date)))
    return dt.datetime.strftime(date, refmt(fmt))


def date_to_str(date, fmt=DATE_DEFAULT_FMT):
    if type(date) == str and date == ACTUALITY_DATE_VALUE:  # проставляем current_date
        date = dt.datetime.now().date()
    elif type(date) == str:
        date = str_to_date(date)
    if type(date) != dt.date:
        raise BaseException('Error conversion {0} to str: wrong type({1})'.format(str(date), type(date)))
    return dt.date.strftime(date, refmt(fmt))


def str_to_type(str_, convert_types=True, inner_quotes=True, date_format=DATE_DEFAULT_FMT,
                datetime_format=DATETIME_DEFAULT_FMT):
    if convert_types:
        if str_.lower() == 'true':
            return True
        if str_.lower() == 'false':
            return False
        if str_.isnumeric():
            return int(str_)
        if str_.count('.') == 1 and str_.replace('.', '').isnumeric():
            return float(str_)
        try:
            return str_to_date(str_.strip('\''), date_format)
        except Exception:
            pass
        try:
            return str_to_datetime(str_.strip('\''), datetime_format)
        except Exception:
            pass
    if inner_quotes:
        return str_.strip('\'').replace('"',"'")
    else:
        return str_.strip('\'')


def is_quoted(str_):
    return str_.count('\'') == 2 and str_[0] == '\'' and str_[len(str_) - 1] == '\''


def _symbol_sort(lst):
    res = dict()    
    word_splitter = max(len(each) for each in lst) + 1
    for each in lst:
        key = word_splitter * each.count(' ') + len(each)
        if key not in res:
            res[key] = list()
        res[key].append(each)
    tmp_sort = list(res.keys())
    tmp_sort.sort(reverse=True)
    res_list = list()
    for each in tmp_sort:
        res_list += res[each]
    return res_list
    

def _str_quotation_split(str_, inner_quotes=True):
    fnd = str_.find('\'')
    res = list()
    if fnd == -1:
        res.append(str_)
        return res
    tmp_word = ''
    counter = 0
    while fnd != -1:
        counter += 1
        if counter % 2 == 1:
            tmp_word = str_[:fnd].strip()
            str_ = str_[fnd + 1:]
        else:
            if inner_quotes:
                if fnd + 1 < len(str_) - 1 and str_[fnd + 1] == "'":
                    counter += 1
                    str_ = str_[:fnd] + '"' + (str_[fnd + 1:][1:])
                else:
                    res.append(tmp_word)
                    res.append("'" + str_[:fnd] + "'")
                    str_ = str_[fnd + 1:]
            else:
                res.append(tmp_word)
                res.append("'" + str_[:fnd] + "'")
                str_ = str_[fnd + 1:]
                
        fnd = str_.find("'")
    if counter % 2 != 0:
        raise ValueError('SmartSplit: string qoutation splitter error: Unclosed quotation mark in {}'.format(str_))
    if str_ != '':
        res.append(str_)
    return res

    
def _str_split(str_, symbol, symbol_list, delimiter=False, pass_qouted=True):
    if is_quoted(str_) and pass_qouted:
        return str_
    if symbol_list is not None:
        if str_ in symbol_list:
            return str_
    if delimiter:
        return str_.split(symbol)
    else:
        tmp_str = str_
        result = list()
        fnd = tmp_str.find(symbol)
        while fnd != -1:
            if fnd != 0:
                result.append(tmp_str[:fnd])
            result.append(symbol)
            tmp_str = tmp_str[fnd + len(symbol):]
            fnd = tmp_str.find(symbol)
        if tmp_str != '':
            result.append(tmp_str)
        return result
        

def _obj_split(obj_, symbol, symbol_list, delimiter=False, pass_qouted=True):
    if type(obj_) == str:
        return _str_split(obj_, symbol, symbol_list, delimiter, pass_qouted)
    elif type(obj_) == list:
        res = list()
        for each in obj_:
            tmp_res = _str_split(each, symbol, symbol_list, delimiter, pass_qouted)
            if type(tmp_res) == str:
                res.append(tmp_res)
            else:
                res = res + tmp_res
        return res
    else:
        raise ValueError('SmartSplit: object splitter error: Only strings and lists are allowed!')


def _str_list_cleaner(obj_):
    res = list()
    for each in obj_:
        if each.strip() != '':
            res.append(each.strip())
    return res


def _str_list_to_type(obj_, convert_types, inner_quotes, date_format, datetime_format):
    result = list()
    for each in obj_:
        result.append(str_to_type(each, convert_types, inner_quotes, date_format, datetime_format))
    return result


def smart_split(str_, symbol_list=None, delimiter_list=None, do_quotation_split=True,
                do_clean=True, convert_types=True, inner_quotes=True, date_format=DATE_DEFAULT_FMT,
                datetime_format=DATETIME_DEFAULT_FMT):
    if not do_quotation_split and inner_quotes:
        inner_quotes = False
    if do_quotation_split and (type(symbol_list) in (str, list, tuple) and len(symbol_list) > 0
            or symbol_list is None):
        result = _str_quotation_split(str_, inner_quotes)
    else:
        result = str_
    if symbol_list is not None:
        if type(symbol_list) == str:
            tmp = list()
            tmp.append(symbol_list)
            symbol_list = tmp
        if len(symbol_list) != 0:
            sorted_list = _symbol_sort(symbol_list)
            for symbol in sorted_list:
                result = _obj_split(result, symbol, symbol_list)
        else:
            result = result.split()
    if delimiter_list is not None:
        for each in delimiter_list:
            result = _obj_split(result, each, symbol_list, delimiter=True)
    if do_clean and type(result) == list:
        result = _str_list_cleaner(result)
    if (convert_types or inner_quotes) and type(result) == list :
        result = _str_list_to_type(result, convert_types, inner_quotes, date_format, datetime_format)
    return result



if __name__ == '__main__':
    test_str_5 = "1=0 and 1 not is not none in '''2'''  and '2' = '' or some_attr = '''2012-12-31'''or('2018-01-01' < '2018-01-02') and self_name is none ('22','33','44')"
    test_str_6 = "'''1014 - 33 - 33'''"
    oper_list = ['<', '>', '=', '<=', '>=', '<>', 'in', 'not in', 'like', 'and', 'or', 'not', 'is none', 'is not none',
                 '+', '-', '*', '/', '**']
    test_res = smart_split(test_str_5, oper_list)
    print(test_str_5)
    print(smart_split(test_str_5, oper_list, ' \t\n'))
    # print(test_res)