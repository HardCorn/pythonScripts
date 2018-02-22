import utility as ut
import operations as op


def check_type(obj_):
    if type(obj_) not in (tuple, list):
        raise ut.ListOperationError('Object {0} not supported in this module ({1})'.format(obj_, type(obj_)))


def find_obj(lst_, obj_, start_=0, list_obj=False):
    check_type(lst_)
    if list_obj:
        check_type(obj_)
    for num in range(start_, len(lst_)):
        if not list_obj and lst_[num] == obj_:
            return num
        elif list_obj and lst_[num] in obj_:
            return num
    return -1
    

def find_all_obj(lst_, obj_, list_obj=False):
    check_type(lst_)
    if list_obj:
        check_type(obj_)
    res = list()
    start = find_obj(lst_, obj_, 0, list_obj)
    while start != -1:
        res.append(start)
        start = find_obj(lst_, obj_, start + 1, list_obj)
    return res
    
    
def replace_sublist(lst_, start_, end_, obj_):
    check_type(lst_)
    res = lst_[:start_] 
    res.append(obj_)
    res += lst_[end_ + 1:]
    return res
    

def tuple_from_list(lst_, fltr_=None, return_list=False, include_mode=False):
    if fltr_ is None:
        res = lst_
    else:
        if type(fltr_) == str:
            fltr = list()
            fltr.append(fltr_)
        else:
            check_type(fltr_)
            fltr = fltr_
        res = list()
        for each in lst_:
            if bool(each not in fltr) ^ bool(include_mode):
                res.append(each)
    if return_list:
        return res
    else:
        return tuple(res)
        

def max_(lst_, fltr=None):
    ls = lst_
    ls.sort()
    if fltr is None:
        try:
            return ls[len(ls) - 1]
        except KeyError:
            return None
    mx = None
    for each in ls:
        if each < fltr:
            mx = each
        else:
            return mx
    return mx
            
            
def min_(lst_, fltr=None):
    ls = lst_
    ls.sort(reverse=True)
    if fltr is None:
        try:
            return ls[len(ls) - 1]
        except KeyError:
            return None
    mx = None
    for each in ls:
        if each > fltr:
            mx = each
        else:
            return mx
    return mx
    
    
def _valid_list_struct(lst_, start_symb='(', delim_symb=',', end_symb=')'):
    if find_obj(lst_, end_symb) != len(lst_) - 1:
        raise ut.ListOperationError('Not valid structure: end-structure symbol found not in the end of struct')
    if find_obj(lst_, start_symb, 1) != -1:
        raise ut.ListOperationError('Not valid structure: start-structure symbol found not in the start of struct')
    st = 2
    while st < len(lst_) - 1:
        if lst_[st] != delim_symb:
            raise ut.ListOperationError(f'Not valid structure: expected delimiter not found in {st}')
        st += 2
        


def find_list(lst_, start_symb='(', delim_symb=',', end_symb=')', start_=0, return_list=False):
    check_type(lst_)
    if find_obj(lst_, start_symb) == -1 or find_obj(lst_, delim_symb) == -1 \
        or find_obj(lst_, end_symb) == -1:
        return None
    start_list = find_all_obj(lst_, start_symb)
    delim_list = find_all_obj(lst_, delim_symb)
    end_list = find_all_obj(lst_, end_symb)
    delim_list.sort()
    for each in delim_list:
        st = max_(start_list, each)
        en = min_(end_list, each)
        if st is None or en is None:
            continue
        tmp = lst_[st: en + 1]
        try:
            _valid_list_struct(tmp, start_symb, delim_symb, end_symb)
        except ut.ListOperationError:
            continue
        else:
            if return_list:
                return [st, en]
            return (st, en)
    return None
    

def modify_list(lst_, lst_start='(', lst_delim=',', lst_end=')', tuples_mode=True):
    res = lst_
    fnd = find_list(res, lst_start, lst_delim, lst_end)
    fltr_list = [lst_start, lst_delim, lst_end]
    while fnd is not None:
        tuple_ = tuple_from_list(res[fnd[0]:fnd[1]+1], fltr_list, return_list=not tuples_mode)
        res = replace_sublist(res, fnd[0], fnd[1], tuple_)
        fnd = find_list(res, lst_start, lst_delim, lst_end)
    return res