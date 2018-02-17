import exceptions
import os
import utilities
# 1 отрабатывает компоновщик - все использующиеся шаблоны запихивает в один большой, все параметры сует в один словарь
# 2 отрабатывает reader - подстановка по словарю всех параметров


# LINKER_CACHE_FILE_NAME = 'linker.cch'
# READER_CACHE_FILE_NAME = 'reader.cch'
GENERATOR_CACHE_FILE_NAME = 'sqlgen.cch'
SQL_DDL_STATEMENT = ('create', 'drop', 'replace')
SQL_DML_STATEMENT = ('insert', 'update', 'delete', 'merge', 'del')
SQL_SEL_STATEMENTS = ('sel', 'select')


def isiterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def sql_start(row):
    row_tmp = row.lower()
    for each in SQL_DDL_STATEMENT:
        if row_tmp.find(each) != -1:
            return 'ddl'
    for each in SQL_DML_STATEMENT:
        if row_tmp.find(each) != -1:
            return 'dml'
    for each in SQL_SEL_STATEMENTS:
        if row_tmp.find(each) != -1:
            return 'sel'
    return None


def revalidate_file(path):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass


def revalidate_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def evaluate(left, cond, right):
    if cond in ('<>', '!='):
        _type = type(left)
        right = _type(right[0])
        return left != right
    elif cond == '=':
        _type = type(left)
        right = _type(right[0])
        return left == right
    elif cond == '>':
        _type = type(left)
        right = _type(right[0])
        return left > right
    elif cond == '<':
        _type = type(left)
        right = _type(right[0])
        return left < right
    elif cond == '>=':
        _type = type(left)
        right = _type(right[0])
        return left >= right
    elif cond == '<=':
        _type = type(left)
        right = _type(right[0])
        return left <= right
    elif cond == 'not in':
        return left not in right
    elif cond == 'in':
        return left in right


def get_param(param_name, dictionary, template):
    if template in dictionary['template']:
        if param_name in dictionary['template'][template]:
            return dictionary['template'][template][param_name]
        base_template = dictionary['template'][template]['base_template']
        if base_template in ['base']:
            if param_name in dictionary['base'][base_template]:
                return dictionary['base'][base_template][param_name]
    if param_name in dictionary['params']:
        return dictionary['params'][param_name]
    else:
        raise exceptions.TemplateLinkerError('Unknown parameter')


def pseudo_parse(string, dictionary, template, sequence):   #case\if\loop string: <interact><type><condition1><template name1>[<condition2><template name2>...]\n
    _res = '\n'                         #for loops <condition> - param names in dictionary['loop_run_param']
    string = string[len('<interact>')+1:len(string)-2]
    string = string.split('><')
    if string[0] == 'case':
        _iter = 1
        flg = False
        while _iter < len(string) - 1 and not flg:
            cond = string[_iter].split()
            left_flg = True
            left = list()
            right = list()
            condition = ''
            for i in cond:
                if i in ('>', '<', '=', '>=', '<=', 'in', 'not', '!=', '<>'):
                    left_flg = False
                    condition += (' ' + i)
                elif left_flg:
                    left.append(i)
                else:
                    right.append(i)
            left = get_param(left[0], dictionary, template)
            condition = condition.strip()
            flg = evaluate(left, condition, right)
            if flg:
                if _res == '\n':
                    _res = ''
                _res += ('<' + string[_iter + 1] + '>\n')
            _iter += 2
    elif string[0] == 'if':
        cond = string[1].split()
        left_flg = True
        left = list()
        right = list()
        condition = ''
        for i in cond:
            if i in ('>', '<', '=', '>=', '<=', 'in', 'not', '!=', '<>'):
                left_flg = False
                condition += (' ' + i)
            elif left_flg:
                left.append(i)
            else:
                right.append(i)
        left = get_param(left[0], dictionary, template)
        condition = condition.strip()
        if evaluate(left, condition, right):
            _res = ('<' + string[2] + '>\n')
    elif string[0] == 'loop':
        param_names = string[1].split(',')
        for i in range(len(param_names)):
            param_names[i] = param_names[i].strip()
        _res = 'loop<' + string[2] + '>\n'
        err_params = list()
        for param in param_names:
            if param not in dictionary['loop_run_param']:
                err_params.append(param)
        if err_params:
            raise exceptions.TemplateLinkerError('Unkonwn loop parameter called \'{}\' for \'{}\' template'.format('\', \''.join(err_params), template))
        max_ = len(dictionary['loop_run_param'][param_names[0]])
        dictionary['loop'] = dict()
        dictionary['loop']['num'] = max_
        for i in range(0, max_):
            entry = sequence.next()
            key = string[2][9:] + str(entry)
            dictionary['template'][key] = dict()
            if i==0:
                dictionary['loop']['start'] = entry
            try:
                for param in param_names:
                    dictionary['template'][key][param] = dictionary['loop_run_param'][param][i]
            except IndexError:
                raise exceptions.TemplateLinkerError('Loop parameter has different number of values')
    return _res


def interact_parse(string, dictionary, template, sequence): # string: <interact><sql><sql_template><type><condition1><template1>[...]\n
    if string[10:15] != '<sql>':
        return pseudo_parse(string, dictionary, template, sequence)
    string = string[16:len(string)-2]
    string = string.split('><')
    res = '#gateway ' + template + ' in\n<' + string[0] + '>\n'
    res += '#gateway ' + template + ' eval ' + string[1]
    cursor = 2
    res_tmp1 = ''
    res_tmp2 = ''
    while cursor < len(string):
        # res += '#branch' + str(int(cursor/2)) +' ' + template + ' ' + string[1] + ' '+ string[cursor] + '\n<'+ string[cursor + 1] + '>\n'
        res_tmp1 += ' (' + string[cursor] + ') branch' + str(int(cursor / 2)) + ' ' + template
        res_tmp2 += '#branch' + str(int(cursor / 2)) + ' ' + template + '\n<' + string[cursor + 1] + '>\n'
        cursor += 2
    if res_tmp1.find(' (else) ') == -1:
        res_tmp1 += ' (else) gateway '+ template + ' out'
    res += res_tmp1 + '\n' + res_tmp2
    res += '#gateway ' + template + ' out\n'
    return res


def get_output(direction, dictionary, small_dic):
    """dictionary - main metadata dictionary,
        small_dic - current row dictionary"""
    if direction == 'parent':
        parent = dictionary['template'][small_dic['template']]['parent']
        return dictionary['template'][parent]['output']
    if direction == 'next':
        params = ['next_template', 'next_sql', 'next']
    elif direction == 'prev':
        params = ['prev_template', 'prev_sql', 'prev']
    else:
        raise exceptions.ScriptGeneratorError('Unknown direction \'{}\''.format(direction))
    if small_dic[params[0]] is None or small_dic[params[1]] is None or \
                    dictionary['sql_chain'][small_dic[params[1]]]['type'] == 'sel':
        raise exceptions.ScriptGeneratorError(
            'There are no {} ddl or dml queries for {} template'.format(params[2], small_dic['template']))
    try:
        return dictionary['template'][small_dic[params[0]]]['output']
    except KeyError:
        raise exceptions.ScriptGeneratorError(
            'There are no output attribute for {} template'.format(small_dic[params[0]]))


class TemplateLinker:
    def __init__(self, tmp_path='cache\\linker\\', template_path='template\\', seq_num=0):
        revalidate_path(tmp_path)
        revalidate_path(template_path)
        self.tmp_path = tmp_path
        self.template_path = template_path
        self.sequence = utilities.Sequence(seq_num)

    def refactor(self, template, dictionary, temp_file, chain, sequence, add='', parent=None):
        """base template refactoring procedure:
            recursive lookup all linked template files and dump pre-sql into one long script"""
        if template not in chain:
            chain.append(template)                              #because of recursive
        else:
            raise exceptions.TemplateLinkerError('Infinite loop gereated. Link template \'{0}\': '.format(chain[0])
                                + 'step \'{0}\', next step is \'{1}\', '.format(chain[len(chain)-1], template)
                                + 'link chain: {0}. '.format('-'.join(chain)))
        template_path = self.template_path + template + '.template'
        append = add
        if add == '':
            append = str(sequence.next())
        base_template = template
        template = template + append
        if template not in dictionary['template']:
            dictionary['template'][template] = dict()
        dictionary['template'][template]['parent'] = parent
        dictionary['template'][template]['base_template'] = base_template
        with open(template_path, 'r') as template_file:
            temp_file.seek(0, 2)
            temp_file.write('#' + template + '\n')
            row = template_file.readline()
            template_type = row[1:len(row)-1]
            if template_type in ('simple', 'main', 'meta pseudo', 'meta interact'):
                dictionary['template'][template]['type'] = template_type
            else:
                raise exceptions.TemplateLinkerError('Unexpected template type {}'.format(template_type))
            row = template_file.readline()
            while row != '':
                if row == '\n':
                    pass
                elif row[0] == '#':
                    row = row[1:len(row)-1]
                    key = row[:row.find(':')].lower().strip(' \'"')
                    value = row[len(key)+1:].strip()
                    if len(key) == 0:
                        raise exceptions.TemplateLinkerError(
                            'Illegal sharped parameter (NoName parameter) in \'{}\' template'.format(template))
                    if key != 'required' and key not in dictionary['template'][template]:
                        tmp_value = value.split()
                        if tmp_value[0].strip() not in ('parent', 'main'):
                            dictionary['template'][template][key] = value.strip(' \'"')
                        elif len(tmp_value) >= 2:
                            if tmp_value[0] == 'parent':
                                inner_temp = ' '.join(tmp_value[1:]).strip()
                                if inner_temp in dictionary['template'][parent]:
                                    dictionary['template'][template][key] = dictionary['template'][parent][inner_temp]
                                else:
                                    raise exceptions.TemplateLinkerError(
                                        'Required parameter \'{}\' not found in parent template \'{}\''.format(inner_temp, parent))
                            else:
                                inner_temp = ' '.join(tmp_value[1:]).strip()
                                if inner_temp in dictionary:
                                    dictionary['template'][template][key] = dictionary['params'][inner_temp]
                                else:
                                    raise exceptions.TemplateLinkerError(
                                        'Required parameter \'{}\' not found in parameter dictionary'.format(
                                            inner_temp))
                        elif tmp_value == ['parent']:
                            if key not in dictionary['template'][parent]:
                                raise exceptions.TemplateLinkerError(
                                    'Required parameter \'{}\' not found in parent template \'{}\''.format(key, parent))
                            else:
                                dictionary['template'][template][key] = dictionary['template'][parent][key]
                        elif tmp_value == ['main']:
                            if key not in dictionary:
                                raise exceptions.TemplateLinkerError(
                                    'Required parameter \'{}\' not found in parameter dictionary'.format(key))
                            else:
                                dictionary['template'][template][key] = dictionary['params'][key]
                        else:
                            raise exceptions.TemplateLinkerError(
                                'Unknown Error "strange sharped parameter in \'{}\' template" (Errno U1)'.format(template))
                    elif value not in dictionary['params'] and key == 'required':
                        raise exceptions.TemplateLinkerError('Required parameter \'{}\' not found'.format(value))
                else:
                    if template_type == 'simple':                                           # simple = just rewrite
                        temp_file.write(row)
                    elif template_type in ('main', 'meta pseudo', 'meta interact'):         # main = rewrite with simple linking
                        if template_type == 'meta pseudo':                                  # meta pseudo = rewrite with some conditions
                            row = pseudo_parse(row, dictionary, template, sequence)                   # meta interact = rewrite with runtime sql-using conditions
                        elif template_type == 'meta interact':
                            row = interact_parse(row, dictionary, template, sequence)
                        partition = '<template'
                        if row.find(partition) == -1:
                            temp_file.write(row)
                        else:
                            if row[:4] == 'loop' and 'loop' in dictionary:
                                loop_start = dictionary['loop']['start']
                                loop_iterations = loop_start + dictionary['loop']['num']
                                for i in range(loop_start, loop_iterations):
                                    tmp_row = row[len('loop<template ') : len(row) - 2]
                                    temp_file.write('\n')
                                    self.refactor(tmp_row, dictionary, temp_file, chain, sequence, str(i), template)
                                    temp_file.seek(0, 2)
                                    temp_file.write('#' + template + '\n')
                                del dictionary['loop']
                            else:
                                while row.find(partition) != -1:
                                    tmp_row, partition, row = row.partition(partition)
                                    temp_file.write(tmp_row)
                                    tmp_row = row[:row.index('>')].strip()
                                    temp_file.write('\n')
                                    self.refactor(tmp_row, dictionary, temp_file, chain, sequence, add, parent=template)
                                    temp_file.seek(0, 2)
                                    temp_file.write('#' + template + '\n')
                                    row = row[row.index('>')+1:]
                                temp_file.write(row)
                    elif template_type == 'meta pseudo':    #rewrite with base logic (based only on parameters)
                        pass
                    elif template_type == 'meta interact':  #rewrite with logic (based on parameters or sql queries)
                        pass
                row = template_file.readline()
        temp_file.write('\n')
        if parent is not None:
            for key in dictionary['template'][parent]:
                if key not in dictionary['template'][template]:
                    dictionary['template'][template][key] = dictionary['template'][parent][key]
        chain.pop()

    def link(self, template, dictionary):
        chain = list()
        tmp_path = self.tmp_path + str(self.sequence.next())
        num = utilities.Sequence()
        with open(tmp_path, 'w') as temp_file:
            self.refactor(template, dictionary, temp_file, chain, num)
        return tmp_path


class ScriptGenerator: # ПЕРЕПИСАТЬ С НУЛЯ!!!!
    def __init__(self, tmp_dir='cache\\reader\\', seq=0, template_dir='template\\'):
        revalidate_path(tmp_dir)
        # revalidate_path(template_dir)
        self.temp_path = tmp_dir
        # self.template_path = template_dir
        self.sequence = utilities.Sequence(seq)

    @staticmethod
    def _lookup(path, dictionary):
        chain = list()
        sql = dict()
        row_counter = 0
        seq = utilities.Sequence()
        with open(path, 'r') as f:
            row = f.readline()
            row_counter += 1
            sql_flg = True
            sql_start_flg = False
            num = 0
            while row != '':
                if row[0] != '#':
                    if not sql_start_flg:
                        sql_type = sql_start(row)
                        if sql_type:
                            sql_start_flg = True
                            num = seq.next()
                            if 'queue' not in sql:
                                sql['queue'] = dict()
                            sql['queue'][row_counter] = num
                            sql[num] = {'start': row_counter, 'type': sql_type}
                    if row.find(';') != -1:
                        sql_flg = True
                        if not sql_start_flg:
                            if len(chain) > 0:
                                tmp_chain = chain[len(chain) - 1]
                            else:
                                tmp_chain = 'First'
                            raise exceptions.ScriptGeneratorError('Lookup error', 'Unexpected \';\' ' +
                                                                               'symbol in {} template'.format(tmp_chain))
                        sql[num]['end'] = row_counter
                        sql_start_flg = False
                elif row[:8] == '#gateway' or row[:7] == '#branch':
                    pass
                else:
                    if len(chain) > 0:
                        if 'end' not in chain[len(chain) - 1]:
                            chain[len(chain) - 1]['end'] = row_counter - 1
                    if not sql_flg and len(chain) > 1:
                        chain.pop()
                    template_name = row[1:len(row) - 1]
                    templ = {'name': template_name}
                    templ['start'] = row_counter
                    chain.append(templ)
                    sql_flg = False
                    tmp = f.tell()
                row = f.readline()
                row_counter += 1
            if len(chain) > 0:
                if 'end' not in chain[len(chain) - 1]:
                    chain[len(chain) - 1]['end'] = row_counter - 1
            if not sql_flg and len(chain) > 1:
                chain.pop()
        map_sql = 0
        map_template = -1
        result_map = list()
        for i in range(1, row_counter):
            if i in sql['queue']:
                map_sql = sql['queue'][i]
            if len(chain) > map_template + 1:
                if chain[map_template + 1]['start'] < i:
                    map_template += 1
            if chain[map_template]['end'] >= i and map_template >= 0:
                tmp_dict = {'template': chain[map_template]['name']}
            else:
                tmp_dict = {'template': None}
            prev_ = None
            next_ = None
            if map_template > 0:
                prev_ = chain[map_template - 1]['name']
            if map_template + 1 < len(chain):
                next_ = chain[map_template + 1]['name']
            tmp_dict['prev_template'] = prev_
            tmp_dict['next_template'] = next_
            sql_query = None
            prev_sql = None
            next_sql = None
            if map_sql > 0:
                if i <= sql[map_sql]['end']:
                    sql_query = map_sql
                if map_sql > 1:
                    prev_sql = map_sql - 1
                if map_sql + 1 in sql:
                    next_sql = map_sql + 1
            else:
                next_sql = 2
            tmp_dict['sql_query'] = sql_query
            tmp_dict['prev_sql'] = prev_sql
            tmp_dict['next_sql'] = next_sql
            result_map.append(tmp_dict)

        # dictionary['template_chain'] = chain
        del sql['queue']
        dictionary['sql_chain'] = sql
        dictionary['template_map'] = result_map

    def create_script(self, path, dictionary):
        self._lookup(path, dictionary)
        script_extension = '.sql'
        script_type = 'simple'
        for key in dictionary['template']:
            if isinstance(dictionary['template'][key], dict):
                if 'type' in dictionary['template'][key]:
                    if dictionary['template'][key]['type'] == 'meta interact':
                        script_extension += 'i'
                        script_type = 'interact'
                        break
        output_script = self.temp_path + str(self.sequence.next()) + script_extension
        with open(output_script, 'w') as f:
            row_num = 0
            with open(path, 'r') as pre_script:
                for row in pre_script:
                    small_dic = dictionary['template_map'][row_num]
                    row_num += 1
                    if script_type == 'interact':
                        if row[:8] == '#gateway' or row[:7] == '#branch':
                            f.write(row)
                            continue
                    if small_dic['template'] is None:
                        continue
                    else:
                        tmp_row = ''
                        params = dict()
                        while row.find('>') > row.find('<') >= 0:
                            param_start = row.find('<')
                            param_end = row.find('>')
                            tmp_row += row[:param_start]
                            param = row[param_start + 1 : param_end].split()
                            if len(param) == 0:
                                params['join'] = ''
                            elif len(param) == 1:
                                if param[0].lower() in ('and', 'or', ','):
                                    params['join'] = ' ' + param[0] + ' '
                                elif param[0].lower() == 'output':
                                    try:
                                        tmp_row += dictionary['template'][small_dic['template']]['output']
                                    except KeyError:
                                        raise exceptions.ScriptGeneratorError('Template \'{}\' has no attribute \'output\''.format(small_dic['template']))
                                else:
                                    try:
                                        tmp_param = get_param(param[0], dictionary, small_dic['template'])
                                    except exceptions.TemplateLinkerError:
                                        tmp_row += '<' + param[0] + '>'
                                    else:
                                        if isiterable(tmp_param) and type(tmp_param) != str:
                                            tmp_row += '{}'
                                            if 'rows_cnt' not in params:
                                                params['rows_cnt'] = len(tmp_param)
                                            elif params['rows_cnt'] != len(tmp_param):
                                                raise exceptions.ScriptGeneratorError('Desynchronized rows parameter')
                                            if 'params' not in params:
                                                params['params'] = [tmp_param,]
                                            else:
                                                params['params'].append(tmp_param)
                                        else:
                                            tmp_row += str(tmp_param)
                            elif len(param) == 2:
                                if param[0].lower() == 'output':
                                    if param[1] in ('next', 'prev', 'parent'):
                                        tmp_row += get_output(param[1], dictionary, small_dic)
                                    else:
                                        if param[1] in dictionary['params']:
                                            if 'output' in dictionary['params'][param[1]]:
                                                tmp_row += dictionary['params'][param[1]]['output']
                                            else:
                                                raise exceptions.ScriptGeneratorError('There are no output for {} template'.format(param[1]))
                                        else:
                                            raise exceptions.ScriptGeneratorError('There are no links to {} template in script'.format(param[1]))
                                else:
                                    tmp_row += '<' + ' '.join(param) + '>'
                            elif len(param) == 3:
                                if param[1].lower() in ('sep', 'separator'):
                                    local_join = ' ' + param[2].strip("'") + ' '
                                    try:
                                        tmp_param = get_param(param[0], dictionary, small_dic['template'])
                                    except exceptions.TemplateLinkerError:
                                        tmp_row += '<' + ' '.join(param) + '>'
                                    else:
                                        if isiterable(tmp_param) and type(tmp_param) != str:
                                            tmp_param = local_join.join(tmp_param)
                                            tmp_row += tmp_param
                                        else:
                                            tmp_row += str(tmp_param)
                                else:
                                    tmp_row += '<' + ' '.join(param) + '>'
                            else:
                                tmp_row += '<' + ' '.join(param) + '>'
                            row = row[param_end + 1:]
                        tmp_row += row
                        if 'join' in params:
                            join = params['join']
                            if 'params' in params: # Все это делать если есть join, в обратных случаях 'params' сджойнить через запятую, добавить join по запятой
                                list_rows = list()
                                for i in range(len(params['params'][0])):
                                    row_dict = list()
                                    for j in range(len(params['params'])):
                                        row_dict.append(params['params'][j][i])
                                    list_rows.append(tmp_row.format(*row_dict))
                                tmp_row = join.join(list_rows)
                        else:
                            if 'params' in params:
                                row_dict = list()
                                for i in range(len(params['params'])):
                                    row_dict.append(', '.join(params['params'][i]))
                                tmp_row = tmp_row.format(*row_dict)
                        f.write(tmp_row)
        return output_script


class TemplateSQLGenerator:
    def __init__(self, tmp_link_path='cache\\linker\\', tmp_read_path='cache\\reader\\', template_path='template\\', \
                 cache_path='cache\\', use_cache=False, link_seq=0, read_seq=0):
        revalidate_path(cache_path)
        revalidate_path(template_path)
        revalidate_path(tmp_read_path)
        revalidate_path(tmp_link_path)
        self.cache_dir = cache_path
        self.use_cache = use_cache
        if self.use_cache:
            pass # read cache file and reassign sequences, maybe read dictionary
        self._cr_meta_()
        self.linker = TemplateLinker(tmp_link_path, template_path, link_seq)
        self.reader = ScriptGenerator(tmp_read_path, read_seq)

    def create_script(self, template, output_path=None):
        temp_file = self.linker.link(template, self.dictionary)
        # print(temp_file)
        temp_file = self.reader.create_script(temp_file, self.dictionary)
        # print(temp_file)
        if output_path:
            with open(output_path, 'w') as trg:
                with open(temp_file, 'r') as src:
                    for each in src:
                        trg.write(each)
            temp_file = output_path
        return temp_file

    def set_template_metadata(self, meta_type='params', template_name=None, **kwargs):
        if meta_type == 'params':
            for key_ in kwargs:
                self.dictionary['params'][key_] = kwargs[key_]
            if template_name:
                self.dictionary['params']['template_name'] = template_name
        elif meta_type == 'loop':
            if kwargs:
                self.dictionary['loop_run_param'] = kwargs
            else:
                self.dictionary['loop_run_param'] = dict()
            if template_name:
                self.dictionary['loop_run_param']['template_name'] = template_name
        elif meta_type == 'template':
            if template_name is not None:
                self.dictionary['base'][template_name] = kwargs
            else:
                raise exceptions.TemplateSQLGeneratorError(
                    'Couldn\'t assign template-level parameter: template_name not resolved')
        else:
            raise exceptions.TemplateSQLGeneratorError('Invalid type of metadata for Script Generation')

    def clear_metadata(self):
        self._cr_meta_()

    def _cr_meta_(self):
        self.dictionary = dict()
        self.dictionary['template'] = dict()
        self.dictionary['params'] = dict()
        self.dictionary['base'] = dict()


if __name__ == '__main__':
    # a = TemplateLinker()
    # dic = {'loop_run_param': {'lookup': [1, 2, 3, 4, 5], 'trash': ['k', 'l', 's', 'd', 'm']}, 'try': {'type': 'meta interact', 'output': 'someOtherText'}, 'loop': 5, 'sample0': {'lookup': 1, 'trash': 'k', 'type': 'main', 'output': 'JustText'}, 'sample1': {'lookup': 2, 'trash': 'l', 'type': 'main', 'output': 'JustText'}, 'sample2': {'lookup': 3, 'trash': 's', 'type': 'main', 'output': 'JustText'}, 'sample3': {'lookup': 4, 'trash': 'd', 'type': 'main', 'output': 'JustText'}, 'sample4': {'lookup': 5, 'trash': 'm', 'type': 'main', 'output': 'JustText'}, 'sample': {'type': 'main', 'output': 'JustText', 'pk_atrs': ['1', '2', '3']}}
    # res = a.link('try', dic)
    # print(res)
    # print(dic)

    # dic = {'loop_run_param': {'sample1': [1,2,3,4,5]}}
    # str1 = '<interact><sql><template smth><if><param = 1><template try>\n'
    # print(interact_parse(str1, dic, 'ling'), dic)
    # a = ScriptGenerator()
    # a._lookup('cache\\linker\\1', dic)
    # print(dic['sql_chain'])
    # print(dic['template_chain'])
    # for i in range(len(dic['template_map'])):
    #     print(i + 1, ' = ', dic['template_map'][i])
    # print(a.create_script('cache\\linker\\1', dic))
    # print(dic)
    dic = {'template': {}, 'base': {}, 'loop_run_param': {'output': ['a', 'b', 'c', 'd', 'trp']}, 'params': {'all_atrs': ['pk1', 'pk2', 'info1', 'info2', 'info3'], 'table1': 'P_TECH_PLAN_FACT_ISSUE_DETAIL', 'table2': 'TECH_PLAN_FACT_ISSUE_DETAIL', 'pk_atrs': ['pk1', 'pk2'], 'other_atrs': ['info1', 'info2', 'info3'], 'not_null_field': 'pk1'}}
    a = TemplateSQLGenerator()
    # a.dictionary = dic
    temp_dict = dict(all_atrs=['pk1', 'pk2', 'info1', 'info2', 'info3'], table1='P_TECH_PLAN_FACT_ISSUE_DETAIL', \
                            table2='TECH_PLAN_FACT_ISSUE_DETAIL', pk_atrs=['pk1', 'pk2'], other_atrs=['info1', 'info2', 'info3'], \
                            not_null_field='pk1')
    # a.set_template_metadata(all_atrs=['pk1', 'pk2', 'info1', 'info2', 'info3'], table1='P_TECH_PLAN_FACT_ISSUE_DETAIL', \
    #                         table2='TECH_PLAN_FACT_ISSUE_DETAIL', pk_atrs=['pk1', 'pk2'], other_atrs=['info1', 'info2', 'info3'], \
                            # not_null_field='pk1')
    a.set_template_metadata(**temp_dict)
    a.set_template_metadata(template_name='sample', source='какашка', parameter='\'2017-05-12 22:11:00\'')
    a.set_template_metadata('loop', output=['a', 'b', 'c', 'd', 'trp'], lookup=['s', 'd'], trash=[1,2])
    a.create_script('try')
    for key in a.dictionary:
        if key != 'template_map':
            print(key, a.dictionary[key])
    for i in range(len(a.dictionary['template_map'])):
        print(i + 1, ' = ', a.dictionary['template_map'][i])