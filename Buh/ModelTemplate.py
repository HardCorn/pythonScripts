import modelExceptions as me
import smartSplit as ss
import json
import listOperations as lo
import datetime as dt
import modelUtility as mu


class ModelTemplate:

    class TemplNone:
        pass

    TNone = TemplNone()
    log_func = mu.Decor._logger

    def __init__(self, name, get_logger, attrs=None, partition=None, key=None, delim=None, defaults=None,
                 worker=None, hide=None, load_mode=None):
        self.logger = mu.Logger('ModelTemplate', get_logger)
        self.name = name
        self.attrs = attrs
        self.partition = partition
        self.key = key
        self.delim = delim
        self.defaults = defaults
        self.worker = worker
        self.hide = hide
        self.load_mode = load_mode

    def __str__(self):
        dic = self.compile(False)
        dic['worker'] = self.worker
        return str(dic)

    @log_func()
    def set_delimiter(self, dlm):
        self.logger.debug('set_delimiter', delimiter=dlm)
        self.delim = dlm

    @log_func()
    def set_load_mode(self, mode_):
        self.logger.debug('set_load_mode', load_mode=mode_)
        self.load_mode = mode_

    @log_func()
    def set_model_name(self, name):
        self.logger.debug('set_model_name', _name=name)
        self.name = name

    def get_worker(self):
        return self.worker

    def validate(self):
        if not self.name:
            self.logger.error('validating template', 'Can\'t create model without it\'s name!', me.ModelTemplateException)
            # raise me.ModelTemplateException(self, 'Can\'t create model without it\'s name!')
        if not self.attrs:
            self.logger.error('validating template', 'Can\'t create model without attributes!', me.ModelTemplateException)
            # raise me.ModelTemplateException(self.name, 'Model Template Validation', 'Can\'t create model without attributes!')
        if not self.key:
            self.logger.error('validating template', 'Can\'t create model without key!', me.ModelTemplateException)
            # raise me.ModelTemplateException(self.name, 'Model Template Validation', 'Can\'t create model without key!')

    @log_func()
    def compile(self, validate_flg=True):
        if validate_flg:
            self.validate()
        res = dict()
        res['attrs'] = self.attrs
        res['key'] = self.key
        res['name'] = self.name
        if self.defaults is not None:
            res['defaults'] = self.defaults
        if self.partition is not None:
            res['partition'] = self.partition
        if self.hide is not None:
            res['hide'] = self.hide
        if self.delim is not None:
            res['delim'] = self.delim
        if self.load_mode is not None:
            res['load_mode'] = self.load_mode
        return res

    @log_func()
    def add_attr(self, attr_name, attr_type, key=False, partition=TNone, default=TNone, hide=False):
        self.logger.debug('add_attr', attr_name=attr_name, attr_type=attr_type, key=key,
                          partition=partition, default=default, hide=hide)
        if self.attrs is None:
            self.attrs = dict()
        self.attrs[attr_name] = attr_type
        if key:
            self.set_key(attr_name)
        if not isinstance(partition, self.TemplNone):
            self.add_partition(attr_name, partition)
        if not isinstance(default, self.TemplNone):
            self.add_default(attr_name, default)
        if hide:
            self.hide_attr(attr_name)

    @log_func()
    def set_key(self, attr_name):
        if attr_name not in self.attrs:
            self.logger.error('set_key', 'Attribute \'{0}\' not found!'.format(attr_name), me.ModelTemplateException)
            # raise me.ModelTemplateException(self.name, 'Set model key', 'Attribute \'{0}\' not found!'.format(attr_name))
        self.key = attr_name

    @log_func()
    def add_partition(self, attr_name, attr_fmt):
        self.logger.debug('add_partition', attr_name=attr_name, attr_fmt=attr_fmt)
        if attr_name not in self.attrs:
            self.logger.error('add_partition', 'Attribute \'{0}\' not found!'.format(attr_name), me.ModelTemplateException)
            # raise me.ModelTemplateException(self.name, 'Adding partition', 'Attribute \'{0}\' not found!'.format(attr_name))
        if self.partition is None:
            self.partition = dict()
        self.partition[attr_name] = attr_fmt

    @log_func()
    def add_partitions(self, partitions):
        for each in partitions:
            self.add_partition(each, partitions[each])

    @log_func()
    def add_default(self, attr_name, attr_value):
        self.logger.debug('add_default', attr_name=attr_name, attr_value=attr_value)
        if attr_name not in self.attrs:
            self.logger.error('add_default', 'Attribute \'{0}\' not found!'.format(attr_name), me.ModelTemplateException)
            # raise me.ModelTemplateException(self.name, 'Adding defaults', 'Attribute \'{0}\' not found!'.format(attr_name))
        if self.defaults is None:
            self.defaults = dict()
        self.defaults[attr_name] = attr_value

    @log_func()
    def add_defaults(self, defaults):
        for each in defaults:
            self.add_default(each, defaults[each])

    @log_func()
    def hide_attr(self, attr_name):
        self.logger.debug('hide_attr', attr_name=attr_name)
        if attr_name not in self.attrs:
            self.logger.error('hide_attr', 'Attribute \'{0}\' not found!'.format(attr_name), me.ModelTemplateException)
            # raise me.ModelTemplateException(self.name, 'Hiding attributes', 'Attribute \'{0}\' not found!'.format(attr_name))
        if self.hide is None:
            self.hide = list()
        if attr_name not in self.hide:
            self.hide.append(attr_name)

    @log_func()
    def hide_attrs(self, attrs):
        for each in attrs:
            self.hide_attr(each)


def create_models_from_file(file_path, log_generator, logger : mu.Logger, json_dict_file=False, worker_name=None):
    if not json_dict_file:
        class ParserError(me.ModelTemplateException):
            def __init__(self, *args):
                string = 'Create model from file: ' + file_path + ': invalid script'
                self.args_ = list()
                self.args_.append(string)
                self.args_ += args
                self.args = args

        class InvalidScript(me.ModelTemplateException):
            def __init__(self, *args):
                string = 'Create model from file: ' + file_path + ': invalid script'
                self.args_ = list()
                self.args_.append(string)
                self.args_ += args
                self.args = args

        log_name = 'create model from file'
        models = list()
        symbol_list = ['attr', 'name', 'default', 'hide', 'key', 'delimiter', 'loading mode', ',', 'worker', ';',
                       ')', '(', 'attrs', 'partition']
        delimiter_list = ' \n\t'
        # row = list()
        repeat = True
        attr_flg = False
        # for each in open(file_path, 'r'):
        #     row = row + ss.smart_split(each, symbol_list, delimiter_list)
        with open(file_path, 'r') as f:
            row = ss.smart_split(f.read(), symbol_list, delimiter_list)
        length = len(row) - 1
        current = 0
        tmp_model = ModelTemplate('', log_generator)
        while repeat:
            if current + 1 <= length:
                next_word = row[current + 1]
            else:
                next_word = 'end of script'
            next_keyword = lo.find_obj(row, symbol_list, start_=current + 1, list_obj=True)
            if current > length:
                logger.note(log_name, 'end of script found')
                repeat = False
                if worker_name is not None:
                    tmp_model.worker = worker_name
                models.append(tmp_model)
            elif attr_flg and not tuple_flg:
                logger.note(log_name, 'next attribute parsing (non-tuple mode)')
                if row[current] == ')':
                    logger.note(log_name, 'attributes definition parsing complete')
                    attr_flg = False
                    current += 1
                else:
                    attr_end = lo.find_obj(row, (',', ')'), start_ = current + 1, list_obj=True)
                    if attr_end == -1:
                        logger.error(log_name, 'attribute definition end not found for model {}'.format(tmp_model.name),
                                     InvalidScript)
                        # raise InvalidScript('attribute definition end not found for model {}'.format(tmp_model.name))
                    current += 1
                    if current + 2 > attr_end:
                        logger.error(log_name, 'attribute name and type required! (model {})'.format(
                                tmp_model.name
                            ), InvalidScript)
                        # raise InvalidScript('attribute definition error', 'attribute name and type required! (model {})'.format(
                        #         tmp_model.name
                        #     ))
                    logger.debug(log_name, attr_name=row[current], attr_type=row[current + 1])
                    attr_dict = {'attr_name': row[current]}
                    attr_dict['attr_type'] = row[current + 1]
                    current += 2
                    while current < attr_end:
                        if row[current] == 'hide':
                            logger.note(log_name, 'hide option found')
                            attr_dict['hide'] = True
                            current += 1
                        elif row[current] == 'partition':
                            logger.note(log_name, 'partition option found')
                            if current + 1 < attr_end and (isinstance(row[current + 1], ss.QuotedString) or row[current + 1] is None):
                                attr_dict['partition'] = row[current + 1]
                                current += 2
                            else:
                                logger.error(log_name, 'partition format not found', InvalidScript)
                                # raise InvalidScript('attribute definition error', 'partition format not found')
                        elif row[current] == 'key':
                            logger.note(log_name, 'key option found')
                            attr_dict['key'] = True
                            current += 1
                        elif row[current] == 'default':
                            logger.note(log_name, 'default option found')
                            if current + 1 < attr_end and not isinstance(row[current + 1], ss.Symbol):
                                attr_dict['default'] = row[current + 1]
                                current += 2
                            else:
                                logger.error(log_name, 'attribute definition error: default value not found after \'default\' keyword',
                                             InvalidScript)
                                # raise InvalidScript('attribute definition error: default value not found after \'default\' keyword')
                        else:
                            logger.error(log_name, 'unknown keyword \'{}\''.format(row[current]), InvalidScript)
                            # raise InvalidScript('attribute definition error', 'unknown keyword \'{}\''.format(row[current]))
                    if current != attr_end:
                        logger.error(log_name, 'attribute definition out of bounds (parsing \'attrs\' statement): current = {0} ({2}), attr_end = {1} ({3})'.format(current, attr_end, row[current], row[attr_end]),
                                     ParserError)
                        # raise ParserError('attribute definition out of bounds (parsing \'attrs\' statement)',
                        #                   'current = {0} ({2}), attr_end = {1} ({3})'.format(current, attr_end, row[current], row[attr_end]))
                    tmp_model.add_attr(**attr_dict)
            elif attr_flg:
                logger.note(log_name, 'next attribute parsing (tuple mode)')
                attr_tuple = row[current]
                for each in attr_tuple:
                    curr = 0
                    if len(each) < 2:
                        logger.error(log_name, 'incorrect attribute definition: {}'.format(each), InvalidScript)
                    logger.debug(log_name, attr_name=each[curr], attr_type=each[curr + 1])
                    attr_dict = {'attr_name': each[curr]}
                    attr_dict['attr_type'] = each[curr + 1]
                    curr += 2
                    while curr < len(each):
                        if each[curr] == 'hide':
                            logger.note(log_name, 'hide option found')
                            attr_dict['hide'] = True
                            curr += 1
                        elif each[curr] == 'partition':
                            logger.note(log_name, 'partition option found')
                            if curr + 1 < len(each) and (
                                    isinstance(each[curr + 1], ss.QuotedString) or each[curr + 1] is None):
                                attr_dict['partition'] = each[curr + 1]
                                curr += 2
                            else:
                                logger.error(log_name, 'partition format not found', InvalidScript)
                                # raise InvalidScript('attribute definition error', 'partition format not found')
                        elif each[curr] == 'key':
                            logger.note(log_name, 'key option found')
                            attr_dict['key'] = True
                            curr += 1
                        elif each[curr] == 'default':
                            logger.note(log_name, 'default option found')
                            if curr + 1 < len(each) and not isinstance(each[curr + 1], ss.Symbol):
                                attr_dict['default'] = each[curr + 1]
                                curr += 2
                            else:
                                logger.error(log_name, 'default value not found after \'default\' keyword', InvalidScript)
                                # raise InvalidScript(
                                #     'attribute definition error: default value not found after \'default\' keyword')
                        else:
                            logger.error(log_name, 'unknown keyword \'{}\''.format(row[current]), InvalidScript)
                            # raise InvalidScript('attribute definition error', 'unknown keyword \'{}\''.format(row[current]))
                    tmp_model.add_attr(**attr_dict)
                current += 1
                attr_tuple = False
                attr_flg = False
            elif row[current] == 'attrs':
                logger.note(log_name, 'attrs keyword found')
                if next_word == '(':
                    attr_flg = True
                    tuple_flg = False
                    current += 1
                elif isinstance(next_word, tuple):
                    attr_flg = True
                    tuple_flg = True
                    current += 1
                else:
                    logger.error(log_name, 'expect \'(\' after \'attrs\' keyword, but {} found'.format(next_word), ParserError)
                    # raise ParserError('expect \'(\' after \'attrs\' keyword, but {} found'.format(next_word))
            elif row[current] == 'name':
                logger.note(log_name, 'name keyword found')
                if tmp_model.name == '' and current + 1 <= length:
                    tmp_model.set_model_name(row[current + 1])
                    current += 2
                elif tmp_model.name != '':
                    logger.error(log_name, 'Current model ({}) already has a name'.format(tmp_model.name), InvalidScript)
                    # raise InvalidScript('Current model ({}) already has a name'.format(tmp_model.name))
                else:
                    logger.error(log_name, 'expect a model name after \'name\' keyword, but {} found'.format(next_word), InvalidScript)
                    # raise InvalidScript('expect a model name after \'name\' keyword, but {} found'.format(next_word))
            elif row[current] == 'worker':
                logger.note(log_name, 'worker keyword found')
                if current + 1 <= length:
                    tmp_model.worker = row[current + 1]
                    current += 2
                else:
                    logger.error(log_name, 'expect a worker name after \'worker\' keyword, but {} found'.format(next_word),
                                 InvalidScript)
                    # raise InvalidScript('expect a worker name after \'worker\' keyword, but {} found'.format(next_word))
            elif row[current] == 'attr':
                logger.note(log_name, 'attr keyword found')
                next_model = next_keyword
                if next_model == -1:
                    next_model = length
                if next_model - current < 2:
                    logger.error(log_name, 'incorrect syntax of \'attr\' keyword: \'attr name type\' expected, but {0} found for model {1}'.format(
                                                        'attr' + ' '.join(row[current : next_model]), tmp_model.name), InvalidScript)
                    # raise InvalidScript('incorrect syntax of \'attr\' keyword: \'attr name type\' expected, but {0} found for model {1}'.format(
                    #                                     'attr' + ' '.join(row[current : next_model]), tmp_model.name))
                logger.debug(log_name, attr_name=row[current + 1], attr_type=row[current + 2])
                tmp_model.add_attr(row[current + 1], row[current + 2])
                current += 3
            elif row[current] == 'partition':
                logger.note(log_name, 'partition keyword found')
                pt_dict = dict()
                if not (next_keyword - current == 2 or length - current > 1):
                    logger.error(log_name, 'incorrect partition attribute option value: partition definition not found!',
                                 InvalidScript)
                    # raise InvalidScript('incorrect partition attribute option value', 'partition definition not found!')
                elif not(isinstance(row[current + 1], tuple)):
                    logger.error(log_name, 'incorrect partition attribute option value: invalid syntax: ' +
                                        '\'partition (attr1 fmt1, [attr2 fmt2, ...])\' expected', InvalidScript)
                    # raise InvalidScript('incorrect partition attribute option value', 'invalid syntax',
                    #                     '\'partition (attr1 fmt1, [attr2 fmt2, ...])\' expected')
                for each in row[current + 1]:
                    if not(isinstance(each, tuple) or isinstance(each, list)) or len(each) != 2:
                        logger.error(log_name, 'incorrect partition attribute option value: invalid syntax: ' +
                                            "'partition (attr1 fmt1, [attr2 fmt2, ...])' expected", InvalidScript)
                        # raise InvalidScript('incorrect partition attribute option value', 'invalid syntax',
                        #                     "'partition (attr1 fmt1, [attr2 fmt2, ...])' expected")
                    pt_dict[each[0]] = each[1]
                current += 2
                tmp_model.add_partitions(pt_dict)
            elif row[current] == 'default':
                logger.note(log_name, 'default keyword found')
                df_dict = dict()
                if not (next_keyword - current == 2 or length - current >= 1):
                    logger.error(log_name, 'incorrect default attribute option value: default definition not found!', InvalidScript)
                    # raise InvalidScript('incorrect default attribute option value', 'default definition not found!')
                elif not(isinstance(row[current + 1], tuple)):
                    logger.error(log_name, 'incorrect default attribute option value: invalid syntax: ' +
                                        '\'default (attr1 val1, [attr2 val2, ...])\' expected', InvalidScript)
                    # raise InvalidScript('incorrect default attribute option value', 'invalid syntax',
                    #                     '\'default (attr1 val1, [attr2 val2, ...])\' expected')
                for each in row[current + 1]:
                    if not(isinstance(each, tuple) or isinstance(each, list)) or len(each) != 2:
                        logger.error(log_name, 'incorrect default attribute option value: invalid syntax' +
                                            '\'default (attr1 val1, [attr2 val2, ...])\' expected', InvalidScript)
                        # raise InvalidScript('incorrect default attribute option value', 'invalid syntax',
                        #                     '\'default (attr1 val1, [attr2 val2, ...])\' expected')
                    df_dict[each[0]] = each[1]
                current += 2
                tmp_model.add_defaults(df_dict)
            elif row[current] == 'key':
                logger.note(log_name, 'key keyword found')
                if current + 1 <= length:
                    tmp_model.set_key(row[current + 1])
                    current += 2
                else:
                    logger.error(log_name, 'loading mode name not found after \'loading mode\' keyword', InvalidScript)
                    # raise InvalidScript('loading mode name not found after \'loading mode\' keyword')
            elif row[current] == 'hide':
                logger.note(log_name, 'hide keyword found')
                if next_keyword - current == 2 or (next_keyword == -1 and length - current == 1):
                    hd_list = row[current + 1]
                    tmp_model.hide_attrs(hd_list)
                    current += 2
                else:
                    if next_keyword == -1:
                        next_keyword = length
                    logger.error(log_name, 'incorrect hide attribute option value! \'hide(attr1, attr2,...)\' required, but {} found'.format(
                        'hide ' + ' '.join(row[current: next_keyword])), InvalidScript)
                    # raise InvalidScript('incorrect hide attribute option value! \'hide(attr1, attr2,...)\' required, but {} found'.format(
                    #     'hide ' + ' '.join(row[current: next_keyword])
                    # ))
            elif row[current] == 'loading mode':
                logger.note(log_name, 'loading mode keyword found')
                if current + 1 <= length:
                    tmp_model.set_model_name(row[current + 1])
                    current += 2
                else:
                    logger.error(log_name, 'loading mode name not found after \'loading mode\' keyword', InvalidScript)
                    # raise InvalidScript('loading mode name not found after \'loading mode\' keyword')
            elif row[current] == 'delimiter':
                logger.note(log_name, 'attrs keyword found')
                if current + 1 <= length:
                    tmp_model.set_delimiter(row[current + 1])
                    current += 2
                else:
                    logger.error(log_name, 'key attribute name not found after \'key\' keyword', InvalidScript)
                    # raise InvalidScript('key attribute name not found after \'key\' keyword')
            elif row[current] == ';':
                logger.note(log_name, '\';\' keyword found')
                if worker_name is not None:
                    tmp_model.worker = worker_name
                models.append(tmp_model)
                tmp_model = ModelTemplate('', log_generator)
                current += 1
            else:
                logger.error(log_name, 'unknown keyword \'{}\''.format(row[current]), ParserError)
                # raise ParserError('unknown keyword \'{}\''.format(row[current]))
        return models
    else:
        with open(file_path, 'r') as f:
            return json.load(f)


if __name__ == '__main__':
    a = ModelTemplate('test_template')
    a.add_attr('key_field', 'int', key=True)
    a.add_attr('info_field', 'str')
    a.add_partition('info_field', None)
    a.add_default('info_field', 'something strange')
    a.hide_attr('key_field')
    res = a.compile()
    print(res, a.get_worker())
    b = create_models_from_file('test.json', True)
    print(b)
    curr = dt.datetime.now()
    c = create_models_from_file('test_file_parser.ddl')
    curr2 = dt.datetime.now()
    print(curr2 - curr)
    for each in c:
        print(each.compile())


