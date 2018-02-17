import os
import exceptions
import utilities
import sqlgen

SQL_DDL_STATEMENT = ('create', 'drop', 'replace')
SQL_DML_STATEMENT = ('insert', 'update', 'delete', 'merge', 'del')
SQL_SEL_STATEMENTS = ('sel', 'select')


def uncoment_query(tmp_line, dict):
    if 'quoted' not in dict:
        dict['quoted'] = False
    if 'commented' not in dict:
        dict['commented'] = False
    if 'request_end' in dict:
        del dict['request_end']
    if 'substr' in dict:
        del dict['substr']
    prev_char = ''
    decommented_line = ''
    index_correction = 0
    for it_ in range(len(tmp_line)):
        lit = tmp_line[it_]
        if lit == '\'' and not dict['commented']:
            dict['quoted'] = not dict['quoted']
        elif lit == '-' and prev_char == '-' and not dict['quoted'] and not dict['commented']:
            decommented_line = decommented_line[:it_ - index_correction - 1] + '\n'
            break
        elif lit == '*' and prev_char == '/' and not dict['quoted'] and not dict['commented']:
            decommented_line = decommented_line[:len(decommented_line) - 1]
            dict['commented'] = True
            index_correction += 1
        elif lit == '/' and prev_char == '*' and not dict['quoted'] and dict['commented']:
            dict['commented'] = False
            decommented_line += ' '
            prev_char = ''
            continue
        elif lit == ';' and not dict['commented'] and not dict['quoted']:  # больше 2 запросов в одну строку - не обрабатывает
            dict['request_end'] = it_ - index_correction
            dict['substr'] = tmp_line[it_ + 1:].strip(' \n\t')
            return decommented_line + ';'
        prev_char = lit
        if not dict['commented']:
            decommented_line += lit
        else:
            index_correction += 1
    dict['len'] = len(decommented_line)
    return decommented_line


class ScriptReader:
    """
        SQL script reader:
        using:
            initialization with some file or without it
            open() will open script file
            next() will return next query from the script
                next(param1=val1, param2=val2, ...) for some interaction stages such as branch evaluation
            close() will close file
            EOF - end of file flag
            is_open - script was opend if True else file is closed
            dictionary - metadata dictionary
            string - buffer for script reading
    """
    def __init__(self, current_file=None):
        self.script = current_file
        self._file = None
        self.is_open = False
        self.dictionary = dict()
        self._init_read_md_()
        self.string = ''
        self.EOF = False

    def _brute_close(self):
        try:
            self._file.close()
        except:
            pass
        finally:
            self.is_open = False

    def open(self, file=None):
        if self.is_open:
            self._brute_close()                     # close file before opening new one
        if not file:
            if not self.script:
                raise exceptions.ScriptReaderException('None file couldn\'t be opened')
            else:
                self.is_open = True
                self._file = open(self.script, 'r')
                self.EOF = False
        else:
            self.is_open = True
            self.script = file
            self._file = open(file, 'r')
            self._init_read_md_()
            self.EOF = False

    def close(self):
        self._brute_close()                         # try to close even if self._file is None/already closed/not file

    def _simple(self):
        self.dictionary['type'] = 's'

    def _interactive(self):
        self.dictionary['type'] = 'i'               # type of script: interacitve is 'i' and non-interactive is 's'
        self.dictionary['interaction'] = dict()     # dictionary with information about current stage, params, smth else
        self.dictionary['chain'] = list()           # chain of different levels multi-level interactive scripts
        self.dictionary['repeat'] = False           # repeating because of changing stages

    def _init_read_md_(self):
        """interaction stages:
            -1 - Not interactive template           (don't use anywhere)
            0 - None interactive                    (simple sending queries - after 4 (or 3) stage or before 1st stage)
            1 - sending query used for interaction  (found #gateway {} in and sending it's queries)
            2 - evaluation                          (found #gateway {} eval...)
            3 - execute current branch              (searching #banchNUM {} and sending it's queries only while not found gateway out or next branch)
            4 - looking for exit part               (searching #gateway {} out if 3rd stage found next branch)"""
        if self.script is not None:
            if self.script[-5:] != '.sqli':
                self._simple()
            else:
                self._interactive()
        # self.dictionary['interaction']['template_name'] = {'stage': 0, 'params': {'param1': val1, 'param2: val2}}

    def is_interactive(self):
        return self.dictionary['type'] == 'i'

    def current(self):
        n = len(self.dictionary['chain']) - 1
        if n < 0:
            return None
        return self.dictionary['chain'][n]

    def current_stage(self):
        if not self.is_interactive():
            return -1
        curr = self.current()
        if curr:
            return self.dictionary['interaction'][curr]['stage']
        else:
            return 0

    def next_i(self, param_flg):
        # current = self.current()
        stage = self.current_stage()
        curr = self.current()
        if stage == 0:
            if self.string != '':
                return self.next_s
            temp_line = self._file.readline()
            if temp_line[:8] == '#gateway':
                split_line = temp_line.strip(' \n\t').split()
                # for i in range(len(split_line)):
                #     split_line[i] = split_line[i].strip('\n')
                if len(split_line) != 3:
                    raise exceptions.ScriptReaderException(
                        'Unknown gateway command: \'{}\' for current stage (0)'.format(temp_line))
                if split_line[2] == 'in':
                    self.dictionary['interaction'][split_line[1]]['stage'] = 1
                    self.dictionary['repeat'] = True
                    self.dictionary['chain'].append(split_line[1])
                    return None
                elif split_line[2] == 'out':
                    raise exceptions.ScriptReaderException(
                        'Unexpected gateway out: \'{}\' for current stage (0)'.format(temp_line))
                elif split_line[2] == 'eval':
                    raise exceptions.ScriptReaderException(
                        'Unexpected gateway eval command: \'{}\' for current stage (0)'.format(temp_line))
                else:
                    raise exceptions.ScriptReaderException('Unknown gateway command: \'{}\''.format(temp_line))
            elif temp_line[:7] == '#branch':
                raise exceptions.ScriptReaderException(
                    'Unexpected branch (\'{}\'): there are no opened gateway'.format(temp_line))
            elif temp_line[0] == '#':
                raise exceptions.ScriptReaderException('Unknown interaction command: \'{}\''.format(temp_line))
            else:
                self.string = temp_line
                return self.next_s
        elif stage == 1:
            pass
        elif stage == 2:
            pass
        elif stage == 3:
            pass
        elif stage == 4:
            temp_line = self._file.readline()
            if temp_line == '':
                self.EOF = True
                raise exceptions.ScriptReaderException('There are no exit for \'{}\' interaction'.format(curr))
            while temp_line != '#gateway ' + curr + ' out':
                temp_line = self._file.readline()
                if temp_line == '':
                    self.EOF = True
                    raise exceptions.ScriptReaderException('There are no exit for \'{}\' interaction'.format(curr))
            self.dictionary['interaction'][curr]['stage'] = 0
            self.string = ''
            self.dictionary['repeat'] = True
            self.dictionary['chain'].pop()
        elif stage == -1:
            return self.next_s
        else:
            raise exceptions.ScriptReaderException('Unknown stage \'{}\''.format(stage))


    @property
    def next_s(self):
        """
            dic - property container:
                len                 - last returned string length
                request_end         - request end index in current line
                commented           - flag for ignoring spec symbols in commentaries
                quoted              - flag for ignoring spec symbols in quotations
                substr              - input string substring which hasn't been checked because of end the of sql request
        """
        dic = dict()
        self.string = uncoment_query(self.string, dic)
        if 'request_end' in dic:
            tmp = self.string     #[:dic['request_end'] + 1]
            self.string = dic['substr']
            return tmp
        else:
            while 'request_end' not in dic and not self.EOF:
                tmp = self._file.readline()
                if tmp == '':
                    self.EOF = True
                elif tmp[0] == '#':
                    raise exceptions.ScriptReaderException(
                        'Unexpected interaction command \'{}\' in non-interaction stage'.format(tmp))
                self.string += ' '+ uncoment_query(tmp, dic)
            tmp = self.string
            if not self.EOF:
                self.string = dic['substr']
            else:
                self.string = ''
            return tmp

    # def next_s_err(self):
    #     # query = self.string
    #     # ind = query.find(';')
    #     query = ''
    #     ind = -1
    #     req_end_flg = False
    #     comment_flg = False
    #     quoted_flg = False
    #     tmp_ln = 0
    #     break_flg = False
    #     substr = ''
    #     first = True
    #     tmp_line = ''
    #     while not req_end_flg and (not self.EOF or self.string != ''):
    #         req_end_flg = False
    #         ind = -1
    #         if first:       #infinite loop
    #             tmp_line = self.string
    #             self.string = ''
    #         if tmp_line == '' or not first:
    #             tmp_line = self._file.readline()
    #             first = False
    #         if tmp_line == '':
    #             self.EOF = True
    #         print(tmp_line)
    #         prev_char = ''
    #         index_correction = 0
    #         decommented_line = ''
    #         for i in range(len(tmp_line)):
    #             lit = tmp_line[i]
    #             if lit == '\'' and not comment_flg:
    #                 quoted_flg = not quoted_flg
    #             elif lit == '-' and prev_char == '-' and not quoted_flg and not comment_flg:
    #                 decommented_line = decommented_line[:i - index_correction - 1] + '\n'
    #                 break
    #             elif lit == '*' and prev_char == '/' and not quoted_flg and not comment_flg:
    #                 decommented_line = decommented_line[:len(decommented_line) - 1]
    #                 comment_flg = True
    #                 index_correction += 1
    #             elif lit == '/' and prev_char == '*' and not quoted_flg and comment_flg:
    #                 comment_flg = False
    #                 decommented_line += ' '
    #                 prev_char = ''
    #                 continue
    #             elif lit == ';' and not comment_flg and not quoted_flg: # больше 2 запросов в одну строку - не обрабатывает
    #                 req_end_flg = True
    #                 ind = i
    #                 break_flg = True
    #                 substr = tmp_line[i+1:]
    #                 break
    #             prev_char = lit
    #             if not comment_flg:
    #                 decommented_line += lit
    #             else:
    #                 index_correction += 1
    #         if break_flg and not comment_flg:
    #             decommented_line += ';'
    #         else:
    #             self.string = ''
    #         tmp_line = decommented_line  #теряем второй запрос
    #         tmp_ln = len(query)
    #         query += tmp_line
    #         if tmp_line == '' and not comment_flg:
    #             query += ';'
    #     if ind == -1:
    #         ind = len(query) - 1
    #     else:
    #         ind += tmp_ln
    #     self.string = query[ind + 1:] + substr #все сломал
    #     query = query[:ind + 1]
    #     if self.string == '\n':
    #         self.string = ''
    #     elif self.EOF and query in ('', '\n', ';'):
    #         query = ';'
    #     return query

    def set_params(self, **kwargs):
        curr = self.current()
        if curr:
            if 'params' not in self.dictionary['interaction'][curr]:
                self.dictionary['interaction'][curr]['params'] = dict()
            for each in kwargs:
                self.dictionary['interaction'][curr]['params'][each] = kwargs[each]
            return True
        return False

    def next(self, **kwargs):
        try:
            if not self.is_interactive():
                res = self.next_s
            else:
                param_flg = self.set_params(**kwargs)
                res = self.next_i(param_flg)
                while self.dictionary['repeat']:
                    param_flg = self.set_params(**kwargs)
                    res = self.next_i(param_flg)
            return res
        except exceptions.EOF:
            self.EOF = True
            return ''


if __name__ == '__main__':
    a = ScriptReader('cache\\reader\\1.sql')
    a.open()
    i = 1
    while not a.EOF:
        print(i, ': ')
        print(a.next())
        print(a.string, len(a.string))
        i += 1
    a.close()