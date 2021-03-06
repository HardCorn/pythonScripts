import expressions as exp
import modelExceptions as me
import dates as dt
from functools import wraps
import os
import logFile as lf


class MainLog(lf.BaseSingletonTextFile):
    def log_start(self):
        self.write('\n' + '*' * 30 + 'log opened at ' + dt.datetime_to_str(dt.datetime.now()) + '*' * 30 + '\n\n')

    def log_end(self):
        self.write('\n' + '*' * 30 + 'log closed at ' + dt.datetime_to_str(dt.datetime.now()) + '*' * 30 + '\n\n')

    def logging_err(self):
        self.write('\n' + '*' * 28 + ' error occured at ' + dt.datetime_to_str(dt.datetime.now()) + '*' * 28 + '\n\n')

    def log_reopen(self):
        self.write('\n' + '*' * 29 + 'log reopened at ' + dt.datetime_to_str(dt.datetime.now()) + '*' * 29 + '\n\n')


def get_meta_path(home_dir):
    return os.path.join(home_dir, 'Metadata') + os.path.sep


def get_data_path(home_dir):
    return os.path.join(home_dir, 'Data') + os.path.sep


def get_worker_path(home_dir, worker_name):
    data_path = get_data_path(home_dir)
    return os.path.join(data_path, worker_name) + os.path.sep


def get_log_dir(home_dir):
    return os.path.join(home_dir, 'Log')


def get_log_path(home_dir):
    log_path = get_log_dir(home_dir)
    return os.path.join(log_path, 'main_log.log')


def get_log_file(log_path):
    return lf.get_log_file(MainLog, log_path)


def build_simple_view(list_str, key):
    fkey = key - 1
    if fkey == 0:
        fval = 1
    else:
        fval = 0
    res_dict = dict()
    for each in list_str:
        res_dict[each[fkey]] = each[fval]
    return res_dict


class Logger:
    def __init__(self, name, get_log_generator):
        self.name = name
        self.logger = next(get_log_generator)
        # self.log_file = log_path
        # with open(self.log_file, 'a'):
        #     pass                    # просто для проверки валидности пути

    def log(self, *msg):
        if len(msg) < 1:
            raise me.UtilityException('Logger Exception', 'there are no log messages to write')
        else:
            msg = list(msg)
            msg[len(msg) - 1] = msg[len(msg) - 1] + '\n'
        write_list = [dt.datetime_to_str(dt.dt.datetime.now()), self.name] + msg
        self.logger.write(': '.join(write_list))
        # with open(self.log_file, 'a') as f:
        #     f.write(': '.join(write_list))

    def debug(self, name, **kwargs):
        tmp_str = name + ': DEBUG: '
        if len(kwargs) < 1:
            raise me.UtilityException('Logger Exception', 'there are no attributes for logging')
        for each in kwargs:
            tmp_str += str(each) + ': ' + str(kwargs[each]) + '; '
        self.log(tmp_str)

    def note(self, name, msg):
        self.log(name, 'Note', msg)

    def error(self, name, msg, exception=None):
        self.log(name, 'Error', msg)
        if issubclass(exception, BaseException):
            forced = True
        else:
            forced = False
        # self.logger.close(forced=forced)
        self.logger.logging_err()
        self.logger.dump_buffer()
        if issubclass(exception, BaseException):
            raise exception(name, msg)


class Decor:
    @staticmethod
    def _logger(name=None, default_debug=False):
        def decorator(function_):
            @wraps(function_)
            def wrapper(*args, **kwargs):
                args[0].logger.log(name_redefine(function_, name), 'start')
                if default_debug:
                    # args[0].logger.debug(function_.__name__, **function_.__dict__)
                    kw_cp = kwargs.copy()
                    if 'name' in kw_cp:
                        kw_cp['_name_'] = kw_cp['name']
                        del kw_cp['name']
                    args[0].logger.debug(function_.__name__, positional_arguments=args[1:], **kw_cp)
                res = function_(*args, **kwargs)
                args[0].logger.log(name_redefine(function_, name), 'ended successfully')
                return res
            return wrapper
        return decorator

    @staticmethod
    def _check_closed(function_):
        @wraps(function_)
        def wrapped(*args, **kwargs):
            if args[0].closed:
                raise me.ModelManagerException('_check_closed decorator', 'operation on closed model!')
            return function_(*args, **kwargs)
        return wrapped


def logger(logger_, name=None):
    def decorator(function_):
        @wraps(function_)
        def wrapper(*args, **kwargs):
            logger_(name_redefine(function_, name), 'start', 'dd')
            res = function_(*args, **kwargs)
            logger_(name_redefine(function_, name), 'ended successfully')
            return res
        return wrapper
    return decorator


def name_redefine(func_, name=None):
    if name is None:
        return func_.__name__
    return name


class Filter:
    def __init__(self):
        self.expr = None
        self.dictionary = dict()
        self.row_head = None

    def set_clause(self, str_):
        self.expr = exp.parse(str_)

    def set_row_head(self, row_head):
        self.row_head = row_head

    def set_row(self, row_):
        if len(self.row_head) != len(row_):
            raise me.FilterException('Set row', 'desync row with it\'s metadata: row_head: {0}, row: {1}'.format(
                self.row_head, row_
            ))
        self._set_str(row_, self.row_head)

    def _set_str(self, row_, row_head):
        tmp_dic = dict()
        for num in range(len(row_head)):
            tmp_dic[row_head[num]] = row_[num]
        self.dictionary = tmp_dic

    def try_resolve(self):
        if type(self.expr) == bool:
            return self.expr
        try:
            self.expr.reset(dict())
            return self.expr.evaluate()
        except:
            return None

    def resolve(self, row_):
        self.set_row(row_)
        return self.get_result()

    def get_result(self):
        if type(self.expr) == bool:
            return self.expr
        elif isinstance(self.expr, exp.Expression):
            self.expr.reset(self.dictionary)
            return self.expr.evaluate()
        elif self.expr is None:
            raise me.FilterException('Expression is None! Can\'t filter with it!')
        else:
            raise me.FilterException('Unknow expression type {}. Can\'t filter with it!'.format(type(self.expr)))


if __name__ == '__main__':
    str_ = "1 = 0 and 1 not in '' or ('2018-01-01' < '2018-01-02') and self_name is none ('22', '33', '44')"
    a = Filter()
    a.set_clause("date_field = '2018-04-01'")
    n = a.try_resolve()
    a.set_row_head(['date_field'])
    b = a.resolve(['2018-04-01'])
    print(n)
    print(b)
    class logs:

        def log(self, *msg):
            print(msg)
    log = logs()

    @logger(log.log)
    def func(value):
        print('nothing matters', value)
        return value + 1

    i = func(10)
    print(i)

