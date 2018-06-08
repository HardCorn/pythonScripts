"""модуль с операциями над списками"""
import utility as ut


def check_type(obj_):   # проверка типа - весь модуль работает только со списками
    if type(obj_) not in (tuple, list):
        raise ut.ListOperationError('Object {0} not supported in this module ({1})'.format(obj_, type(obj_)))


def find_obj(lst_, obj_, start_=0, end_=None, list_obj=False):  # поиск первого вхождения элемента в список
    """
    Функция ищет первое вхождение объекта в список
    :param lst_: исходный список
    :param obj_: объект который ищем
    :param start_: элемент с которого начинаем искать
    :param end_: элемент до которого ищем
    :param list_obj: флаг, выставлять True если в obj_ передан список объектов а не один объект
    :return: индекс первого входения искомого элемента или -1, если ничего не найдено
    """
    check_type(lst_)
    if end_ is None:
        end_ = len(lst_)
    if list_obj:
        check_type(obj_)
    for num in range(start_, end_):
        if not list_obj and lst_[num] == obj_:
            return num
        elif list_obj and lst_[num] in obj_:
            return num
    return -1
    

def find_all_obj(lst_, obj_, list_obj=False):
    """
    Функция поиска всех объектов в списке
    :param lst_: исходный список
    :param obj_: искомый объект/список объектов
    :param list_obj: флаг, ставим True если передали список объектов в obj_
    :return: список индексов или пустой список, если ничего не найдено
    """
    check_type(lst_)
    if list_obj:
        check_type(obj_)
    res = list()
    start = find_obj(lst_, obj_, 0, None, list_obj)
    while start != -1:
        res.append(start)
        start = find_obj(lst_, obj_, start + 1, None, list_obj)
    return res
    
    
def replace_sublist(lst_, start_, end_, obj_, list_obj=False):
    """
    Функция заминяет часть списка на объект
    :param lst_: исходный список
    :param start_: индекс начала заменяемого списка
    :param end_: индекс конца заменяемого списка
    :param obj_: объект которым заменяется под-список
    :param list_obj: флаг передачи объекта-списка
    :return: список в котором нужны под-список замещен на новый объект
    """
    check_type(lst_)
    if not (0 <= start_ < len(lst_) and 0 <= end_ < len(lst_)) or start_ > end_:
        raise ut.ListOperationError('Incorrect indexes list: {0}, start: {1}, end: {2}'.format(
            lst_, start_, end_
        ))
    res = lst_[:start_]
    if not list_obj:
        res.append(obj_)
    else:
        res += obj_
    res += lst_[end_ + 1:]
    return res
    

def tuple_from_list(lst_, fltr_=None, return_list=False, include_mode=False, ln=1):
    """
    Функция фильтрует список по фильтру и преобразует к кортежу (если это необходимо)
    :param lst_: исходный список
    :param fltr_: список фильтруемых элементов
    :param return_list: флаг возвращения списка
    :param include_mode: флаг работы в режиме include (обратная фильтрация - выбираем только элементы из списка фильтров)
    :return: отфильтрованный кортеж (или список)
    """
    if fltr_ is None:
        res = lst_
    else:
        if type(fltr_) == str:
            fltr = list()
            if fltr_ != '':
                fltr.append(fltr_)
        else:
            check_type(fltr_)
            fltr = fltr_
        res = list()
        for each in lst_:
            if bool(each not in fltr) ^ bool(include_mode):
                res.append(each)
    if ln != 1:
        if len(res) % ln != 0:
            raise ut.ListOperationError('Incorrect element length ({0}) for list {1}'.format(ln, lst_))
        res_tmp = list()
        st = 0
        while st < len(res):
            tmp_ls = list()
            for i in range(ln):
                tmp_ls.append(res[st + i])
            res_tmp.append(tmp_ls)
            st += ln
        res = res_tmp
    if return_list:
        return res
    else:
        return tuple(res)
        

def max_(lst_, low_border=None, high_border=None):
    """
    Функция работает со списками чисел и возвращает максимальный элемент в заданном диапазоне
    :param lst_: исходный список
    :param high_border: верхняя граница заданного диапазона (элеменет строго меньше ее)
    :param low_border: нижняя граница заданного диапазона (элемент строго больше ее)
    :return: None если такого элемента нет или сам элемент
    """
    ls = lst_
    if ls is None or len(ls) == 0: # пустой список
        return None
    ls.sort()
    if high_border is None and low_border is None: # границы не заданы - просто возвращаем максимальный элемент
        return ls[len(ls) - 1]
    if low_border is None:
        low_border = ls[0] - 1
    if high_border is None:
        high_border = ls[len(ls) - 1] + 1
    mx = None
    for each in ls:
        if low_border < each < high_border:
            mx = each
        elif each > high_border:
            return mx
    return mx
            
            
def min_(lst_, low_border=None, high_border=None):
    """
    Функция возвращает минимальный элемент в заднном диапазоне
    :param lst_: исходный список
    :param low_border: нижняя граница заданного диапазона
    :param high_border: верхняя граница заданного диапазона
    :return: минимальный элемент или None
    """
    ls = lst_
    if ls is None or len(ls) == 0:  # из пустого списка - возвращаем None сразу
        return None
    ls.sort(reverse=True)
    if low_border is None and high_border is None:  # если не заданы границы - просто возвращаем самый маленький
        return ls[len(ls) - 1] - 1
    if low_border is None:
        low_border = ls[len(ls) - 1] - 1
    if high_border is None:
        high_border = ls[0] + 1
    mx = None
    for each in ls:
        if low_border < each < high_border:
            mx = each
        elif each < low_border:
            return mx
    return mx
    
    
def _valid_list_struct(lst_, start_symb='(', delim_symb=',', end_symb=')', mv=2):
    """
    Функция падает если заданный спиок не подходит под формат [символ начала, элемент1, символ разделитель,
        элемент2, символ разделитель,..., символ окончания] каждый элемент при этом может быть составым (
        состоять из 1, 2-х и более элементов), но при этом должен иметь фиксированную длину
    :param lst_: исходный символ
    :param start_symb: символ начала списка
    :param delim_symb: символ-разделитель списка
    :param end_symb: символ окончания списка
    :param mv: разница между индексами соседних символов разделителей
    :return: None - падает если входная структура не валидна
    """
    if find_obj(lst_, end_symb) != len(lst_) - 1:   # проверяем начало списка
        raise ut.ListOperationError('Not valid structure: end-structure symbol found not in the end of struct')
    if find_obj(lst_, start_symb, 1) != -1:         # проверяем окончание списка
        raise ut.ListOperationError('Not valid structure: start-structure symbol found not in the start of struct')
    st = mv
    while st < len(lst_) - 1:                       # проверяем что после каждого элемента идет разделитель
        if lst_[st] != delim_symb:
            raise ut.ListOperationError(f'Not valid structure: expected delimiter not found in {st}')
        st += mv


def find_list(lst_, start_symb='(', delim_symb=',', end_symb=')', start_=0, return_list=False):
    """
    Функция поиска структуры подходящей под описание списка с разделителем (не ищем пустых списков)
    :param lst_: исходный список
    :param start_symb: символ начала структуры
    :param delim_symb: символ-разделитель
    :param end_symb: символ окончания структуры
    :param start_: пока не используется - потенциально начальная позиция просмотра
    :param return_list: флаг возврата списка (по умолчанию это кортеж)
    :return: возвращает координаты начала-конца потенциального списка и длину элементов или None если такая струткура не найдена
    """
    check_type(lst_)
    if find_obj(lst_, start_symb) == -1 or find_obj(lst_, delim_symb) == -1 \
        or find_obj(lst_, end_symb) == -1:  # если не находим символов начала/окончания/разделитель - возвращаем None
        return None
    start_list = find_all_obj(lst_, start_symb) # получаем список всех индексов символов-начала
    delim_list = find_all_obj(lst_, delim_symb) # список всех индексов символов-разделителей
    end_list = find_all_obj(lst_, end_symb)     # список всех индексов символов-окончаний
    delim_list.sort()                           # на всякий случай сортируем индексы разделителей
    for each in delim_list:                     # пробегаемся по всем разделителям
        st = max_(start_list, high_border=each) # получаем ближайший к нему снизу символ начала
        en = min_(end_list, each)               # ближайший сверху символ окончания
        if st is None or en is None:            # если кого-то из них нет - ищем дальше
            continue
        tmp = lst_[st: en + 1]                  # формируем список из исходного - потенциально подходящий по структуре
        cnt = tmp.count(delim_symb) + 1
        if tmp[len(tmp) - 2] != delim_symb:   # если после последнего элемента стоит символ разделитель - длины необходимо скорректировать
            mod_len = len(tmp)
            cnt_orig = cnt
        else:
            mod_len = len(tmp) - 1
            cnt_orig = cnt
            cnt -= 1
        if cnt_orig != 0 and len(tmp) != 3:
            if (mod_len - 1) % cnt != 0:        # проверяем что длины элементов фиксированы
                continue
            mv = (mod_len - 1) / (cnt)      # считаем шаг (расстояние между соседними символами разделителями)
        else:                                   # если полученный список состоит только из разделителя - не подходит
            continue
        mv = int(mv)
        try:                                    # проверяем структуру этого списку
            _valid_list_struct(tmp, start_symb, delim_symb, end_symb, mv)
        except ut.ListOperationError:           # не подходит - ищем дальше
            continue
        else:
            if return_list:                     # если подходим - возвращаем координаты
                return [st, en, mv - 1]
            return (st, en, mv -1)
    return None
    

def modify_list(lst_, lst_start='(', lst_delim=',', lst_end=')', tuples_mode=True):
    """
    Функция ищет и подменяет все структуры подходящие под описание списка с разделителями на кортежи/списки
    :param lst_: исходный список
    :param lst_start: символ начала стуктуры
    :param lst_delim: символ-разделитель структуры
    :param lst_end: символ окончания структуры
    :param tuples_mode: True - будем заменять на кортежи, False - заменяем на списки
    :return: исходный список, в котором все подходящие под описание структуры заменены на списки/кортежи
    """
    res = lst_
    fnd = find_list(res, lst_start, lst_delim, lst_end) # ищем подходящую структуру
    fltr_list = [lst_start, lst_delim, lst_end]         # получаем список разделителей
    while fnd is not None:
        tuple_ = tuple_from_list(res[fnd[0]:fnd[1]+1], fltr_list, return_list=not tuples_mode, ln=fnd[2])  # получаем спиок из листа, фильтруя все служебные символы
        res = replace_sublist(res, fnd[0], fnd[1], tuple_)  # подменяем в результирующем списке под-список на полученную структуру
        fnd = find_list(res, lst_start, lst_delim, lst_end) # ищем следующую подходящую структуру
    return res


def filter_list(lst_, fltr_, include=False):
    """
    Функция фильтрации списка
    :param lst_: исходный список
    :param fltr_: фильтр
    :param include: режим включения\выключения элементов фильтра
    :return: пофильтрованный список
    """
    check_type(lst_)
    lst = lst_
    if type(fltr_) == str:
        fltr = list()
        if len(fltr) > 0:
            fltr.append(fltr_)
    else:
        fltr = fltr_
    res = list()
    for each in lst:
        if (each in fltr) == include:
            res.append(each)
    return res


def get_sublist(lst_, start_symb, end_symb):
    """
    Функция получает координаты ближайших друг к другу символов начала и окончания
    :param lst_: исходный список
    :param start_symb: символ начала структуры
    :param end_symb: символ окончания структуры
    :return: координаты начала и окончания
    """
    check_type(lst_)
    st_list = find_all_obj(lst_, start_symb)
    end_list = find_all_obj(lst_, end_symb)
    if len(st_list) == 0 or len(end_list) == 0:
        return None
    for each in end_list:
        st = max_(st_list, high_border=each)
        return (st, each)


if __name__ == '__main__':
    lsta = [1,2,3,4,5,6,7,8,9,0]
    lstb = [2,4,6,8,0]
    # print(filter_list(lsta, lstb, True))
    # list1 = ['(', '(', 1,3,')', 4, '(',5, ')', ')', ')']
    # print(get_sublist(list1, '(', ')'))
    print(min_(lsta, 4, 0), max_(lsta, 11, 8))