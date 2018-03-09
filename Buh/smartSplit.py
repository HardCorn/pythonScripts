import dates as dt
import listOperations as lo


class SmartSplitString(str):
    pass


class Symbol(SmartSplitString):  # Абстрактный класс к которому приводим символы
    pass


class UnConvString(SmartSplitString):    # абстрактный класс к которому приводим неконвертируемые строки
    pass


class QuotedString(SmartSplitString):    # абстактный класс к которому приводим строки в кавычках
    pass


def get_symbol_border_list(symbol_list, delimiter_list):
    tmp = ''
    if symbol_list is not None:
        if isinstance(symbol_list, list):
            for each in symbol_list:
                if len(each) == 1 and not each.isalpha():
                    tmp += each
    if isinstance(delimiter_list, str):
        tmp += delimiter_list
    else:
        tmp += ' \t\n'
    return tmp


def check_symbol_borders(str_, symbol, symb_start_pos, borders):
    if not symbol.isalpha():
        return True
    else:
        if len(str_) > len(symbol):
            if symb_start_pos > 0:
                if str_[symb_start_pos - 1] not in borders:
                    return False
            if len(str_) - 1 > symb_start_pos + len(symbol):
                if str_[symb_start_pos + len(symbol)] not in borders:
                    return False
            return True

        else:
            return True


def str_to_type(str_, convert_types=True, inner_quotes=True, date_format=dt.DATE_DEFAULT_FMT,
                datetime_format=dt.DATETIME_DEFAULT_FMT, symbol_list=None):  # Пытается привести строку к разным типам данных
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
            return dt.str_to_date(str_.strip('\''), date_format)
        except Exception:
            pass
        try:
            return dt.str_to_datetime(str_.strip('\''), datetime_format)
        except Exception:
            pass
        if is_quoted(str_):
            if inner_quotes:
                return QuotedString(str_.strip("'").replace('"', "'"))
            else:
                return QuotedString(str_.strip("'"))
        elif type(symbol_list) in (tuple, list)and str_ in symbol_list:
            return Symbol(str_)
        elif type(symbol_list) == str and str_ == symbol_list:
            return Symbol(str_)
        else:
            return UnConvString(str_)
    if inner_quotes:    # удаляем концевые кавычки и подменяем внутренние двойные кавычки на одинарные, если стоит соотв. флаг
        return str_.strip('\'').replace('"',"'")
    else:               # иначе просто удаляем концевые кавычки
        return str_.strip('\'')


def is_quoted(str_):        # проверка на заковыченную строку
    return str_.count('\'') == 2 and str_[0] == '\'' and str_[len(str_) - 1] == '\''


def _symbol_sort(lst):      # сортировка символов в порядке: кол-во слов по убыванию количество букв выражении по убыванию
    res = dict()    
    word_splitter = max(len(each) for each in lst) + 1  # переменная множитель колличества слов (длина максимальной строки + 1)
    for each in lst:                                    # наполняем временный словарь
        key = word_splitter * each.count(' ') + len(each)
        if key not in res:
            res[key] = list()
        res[key].append(each)
    tmp_sort = list(res.keys())                         # забираем и сортируем ключи по убыванию
    tmp_sort.sort(reverse=True)
    res_list = list()
    for each in tmp_sort:                               # наполняем результирующий список по отсортированным ключам
        res_list += res[each]
    return res_list
    

def _str_quotation_split(str_, inner_quotes=True):      # дробилка одной строки на подстроки заключенные в кавычках - и без них
    fnd = str_.find('\'')
    res = list()
    if fnd == -1:                           # если не нашли ни одной кавычки - возвращаем исходную строку, обернутую в список
        res.append(str_)
        return res
    tmp_word = ''       # буффер для слов до открывающей кавычки
    counter = 0         # счетчик найденных кавычек
    while fnd != -1:
        counter += 1    # нашли новую кавычку
        if counter % 2 == 1:        # если нечетная - открывающая - сохраняем подстроку до нее и обрезаем строку до этой кавычки
            tmp_word = str_[:fnd].strip()
            str_ = str_[fnd + 1:]
        else:                       # если четная (необязательно закрывающая, возможно и экранированная внутри)
            if inner_quotes:
                if fnd + 1 < len(str_) - 1 and str_[fnd + 1] == "'": # если следующая за ней тоже кавычка - то это экран
                    counter += 1                                        # инкрементируем счетчик
                    str_ = str_[:fnd] + '"' + (str_[fnd + 1:][1:])      # аккуратно заменяем две кавычки на двойную кавычку
                else:                                                   # если за ней нет кавычек - то это закрывающая
                    res.append(tmp_word)                                # пишем в результирующий список слово до кавычки
                    res.append("'" + str_[:fnd] + "'")                  # пишем слово в кавычках дополнительно оборачивая его в кавычки
                    str_ = str_[fnd + 1:]                               # обрезаем строку закрывающей кавычкой
            else:                                                       # если не обрабатываем внутренние кавычки
                res.append(tmp_word)
                res.append("'" + str_[:fnd] + "'")
                str_ = str_[fnd + 1:]
        fnd = str_.find("'")                                            # ищем следующую кавычку
    if counter % 2 != 0:                                                # если в итоге нашли нечетное число кавычек - падаем
        raise ValueError('SmartSplit: string qoutation splitter error: Unclosed quotation mark in {}'.format(str_))
    if str_ != '':                                                      # дописываем строку после последней кавычки
        res.append(str_)
    return res

    
def _str_split(str_, symbol, symbol_list, delimiter=False, pass_qouted=True, check_borders=False, borders=None):   # разрезание строки по символу
    if is_quoted(str_) and pass_qouted:         # если получили строку в кавычках - просто возвращаем ее
        return str_
    if symbol_list is not None:                 # если получили один из символов - так же возвращаем его
        if str_ in symbol_list:
            return str_
    if delimiter:                               # если работаем в режиме простого разделителя - пользуемсявстроенной функцией
        return str_.split(symbol)
    else:
        tmp_str = str_
        result = list()
        fnd = tmp_str.find(symbol)              # ищем символ в строке
        while fnd != -1:
            if not check_borders or check_symbol_borders(tmp_str, symbol, fnd, borders):
                if fnd != 0:                        # если он не в начале строки пишем начало строки до символа
                    result.append(tmp_str[:fnd])
                result.append(symbol)               # приписываем сам символ
                tmp_str = tmp_str[fnd + len(symbol):]   # обрезаем строку
                fnd = tmp_str.find(symbol)          # снова ищем
            else:
                fnd = tmp_str.find(symbol, fnd + 1)
        if tmp_str != '':                       # если после последнего символа осталось что-то - дописываем в конец
            result.append(tmp_str)
        return result
        

def _obj_split(obj_, symbol, symbol_list, delimiter=False, pass_qouted=True, check_borders=False, borders=None):   # обертка разрезалки строки - работает со строками и списками строк
    if type(obj_) == str:
        return _str_split(obj_, symbol, symbol_list, delimiter, pass_qouted, check_borders, borders=borders)
    elif type(obj_) == list:
        res = list()
        for each in obj_:
            tmp_res = _str_split(each, symbol, symbol_list, delimiter, pass_qouted, check_borders, borders=borders)
            if type(tmp_res) == str:
                res.append(tmp_res)
            else:
                res = res + tmp_res
        return res
    else:
        raise ValueError('SmartSplit: object splitter error: Only strings and lists are allowed!')


def _str_list_cleaner(obj_):            # очиститель списка - удаляет концевые пробелы/служебные символы и пустые элементы
    res = list()
    for each in obj_:
        if each.strip() != '':
            res.append(each.strip())
    return res


def _str_list_to_type(obj_, convert_types, inner_quotes, date_format, datetime_format, symbol_list): # обертка преобразователя строки к стандартным типам
    result = list()
    for each in obj_:
        result.append(str_to_type(each, convert_types, inner_quotes, date_format, datetime_format, symbol_list))
    return result


def smart_split(str_, symbol_list=None, delimiter_list=None, do_quotation_split=True,
                do_clean=True, convert_types=True, convert_tuples=True, check_symbols=True,
                date_format=dt.DATE_DEFAULT_FMT, datetime_format=dt.DATETIME_DEFAULT_FMT):  # сама разрезалка
    """
    Функция разбирает строку на список:
        а) выражений в кавычках (приводятся к строкам, экранированные кавычки: '' внутри приводятся к обычным кавычкам
            имеют абстрактный тип QuotedString
        б) элементов переданных в список символов(если таковые в строке были)
            имеют абстрактный тип Symbol
        в) всего остального с приведенными типами данных, включая приведение к кортежам
            при этом не изменяя порядок вхождения элементов в исходную строку и очищая каждый элемент от лишних
            концевых пробелов и служебных символов
            Строки из этого пула приводятся к абстрактному типу UnConvString
    Все кастомные строковые типа (QoutedString, Symbol, UnConvString) - строки с базовым классом SmartSplitString -
        оберткой над str, ко всем 4 можно применять все стандартные строковые функции, не забывая, что большинство из них
        автоматически приводит строку к типу str (никакие функции/методы класса str не переписывались)
        обертки созданы только для того чтобы различать строки на выходе.
    :param str_: исходная строка
    :param symbol_list: список элементов-разделителей которые необходимо оставить в результирующем списке; по умолчанию - None
    :param delimiter_list: список символов-разделителей - можно передавать строкой, списком, кортежем - не сохраняются в итоговом списке; по умолчанию - None
    :param do_quotation_split: флаг сохранения заковыченных элементов отдельными элементами списка; по умолчанию - True
    :param do_clean: флаг очищения итогового списка от пустых элементов и служебных символов/концевых пробелов; по умолчанию - True
    :param convert_types: флаг необходимости преобразования базовых типов данных(int, float, date, datetime, bool); по умолчанию - True
    :param convert_tuples: флаг необходимости преобразования структур похожих на кортежи к кортежам внутри списка; по умолчанию - True
    :param check_symbol: Проверка границ символа (чтобы не резать одно слово по вхождению в него элемента-разделителя подстрокой)
    :param date_format: формат представления дат в строке; по умолчанию - YYYY-MM-DD
    :param datetime_format: формат представления даты-времени в строке; по умолчанию - YYYY-MM-DD HH:MI:SS.SSSSSS
    :return: возвращает список
    """
    if str_ == '':
        return []
    if not do_quotation_split:
        inner_quotes = False
    else:
        inner_quotes = True
    if do_quotation_split and (type(symbol_list) in (str, list, tuple) and len(symbol_list) > 0
            or symbol_list is None):    # если неоходимо разрезать по кавычкам - режем
        result = _str_quotation_split(str_, inner_quotes)
    else:
        result = str_
    if symbol_list is not None:         # если на входе получили список символов
        if check_symbols:
            borders = get_symbol_border_list(symbol_list, delimiter_list)
        else:
            borders = None
        if type(symbol_list) == str:    # строку преобразуем к списку
            tmp = list()
            if len(symbol_list) > 0:
                tmp.append(symbol_list)
            symbol_list = tmp
        if len(symbol_list) != 0:
            sorted_list = _symbol_sort(symbol_list) # сортируем символы
            for symbol in sorted_list:              # по полученному списку режем строку
                result = _obj_split(result, symbol, symbol_list, check_borders=check_symbols, borders=borders)
        else:                                       # если на входе получили пустую строку/пустой список - просто делаем split()
            if type(result) == str:
                result = result.split()
    if delimiter_list is not None:                  # если получили список разделителей - нарезаем еще и по ним
        for each in delimiter_list:
            result = _obj_split(result, each, symbol_list, delimiter=True)
    if do_clean and type(result) == list:           # чистим список
        result = _str_list_cleaner(result)
    if (convert_types or inner_quotes) and type(result) == list :   # преобразуем элементы списка
        result = _str_list_to_type(result, convert_types, inner_quotes, date_format, datetime_format, symbol_list)
    if convert_tuples:                              # преобразуем подсписки формата ['(', 1, ',', ..., ')'] к кортежам
        result = lo.modify_list(result)
    return result


if __name__ == '__main__':
    test_str_5 = "1=0 andy 1 not is not none in '''2'''  and '2' = '' or some_attr = '''2012-12-31'''or('2018-01-01' < '2018-01-02') and self_name is none ('22','33','44')"
    test_str_6 = "'''1014 - 33 - 33'''"
    oper_list = ['<', '>', '=', '<=', '>=', '<>', 'in', 'not in', 'like', 'and', 'or', 'not', 'is none', 'is not none',
                 '+', '-', '*', '/', '**', '(', ')']
    test_res = smart_split(test_str_5, oper_list)
    print(test_str_5)
    tst = smart_split(test_str_5, oper_list, ' \t\n')
    for each in tst:
        print(each, ': ', isinstance(each, SmartSplitString), type(each))
    # print(test_res)