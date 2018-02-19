def is_quoted(str_):
    return str_.count('\'') == 2 and str_[0] == '\'' and str_[len(str_) - 1] == '\''


def _input_range(lst):
    res = dict()
    for each in lst:
        key = -1
        if len(each) == 1:
            key = 0
        else:
            key = each.count(' ') + 1
        if key == -1:
            raise ValueError('Unknown error: input range key = -1')
        if key not in res:
            res[key] = list()
        res[key].append(each)
    return res
    

def _str_qoutation_split(str_):
    fnd = str_.find('\'')
    if fnd == -1:
        return str_
    res = list()
    tmp_word = ''
    counter = 0
    while fnd != -1:
        counter += 1
        if counter mod 2 == 1:
            tmp_word = str_[:fnd].strip()
        else:
            res.append(tmp_word)
            res.append("'" + str_[:fnd] + "'")
        str_ = str_[fnd + 1:]
        fnd = str_.find("'")
    if counter mod 2 != 0:
        raise ValueError('Unclosed qoutation mark')
    result.append(str_)
    return results

    
def _str_split(str_, symbol, symbol_list, delimiter=False, pass_qouted=True):
    if is_qouted(str_) and pass_qouted:
        return str_
    if str_ in symbol_list:
        return str_
    if delimiter:
        return str_.split(symbol)
    else:
        tmp_str = str_
        result = list()
        fnd = tmp_str.find(symbol)
        while fnd != -1
            if fnd != 0:
                result.append(tmp_str[:fnd])
            result.append(symbol)
            tmp_str = tmp_str[fnd + len(symbol):]
            fnd = tmp_str.find(symbol)
        result.append(tmp_str)
        

def _obj_split(obj_, symbol, symbol_list, delimiter=False, pass_qouted=True):
    if type(obj_) == str:
        return _str_split(obj_, symbol, symbol_list, delimiter, pass_qouted)
    elif type(obj_) == list:
        res = list()
        for each in obj_:
            res = res + _str_split(each, symbol, symbol_list, delimiter, pass_qouted)
        return res
    else:
        raise ValueError('Any object types except strings and lists are not allowed!')