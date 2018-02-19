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
    while fnd != -1:
        

    
def _str_split(str_, symbol, delimiter=False, pass_qouted=True):
    if is_qouted(str_) and pass_qouted:
        return str_
    if delimiter:
        return str_.split(symbol)
    else:
        tmp_str = str_
        result = list()
        fnd = tmp_str.find(symbol)
        if fnd == -1:
            return result.append(str_)
        while fnd != -1
            if fnd != 0:
                result.append(tmp_str[:fnd])
            result.append(symbol)
            tmp_str = tmp_str[fnd + len(symbol):]
            fnd = tmp_str.find(symbol)