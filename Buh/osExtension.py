import os
import functools as ft
import datetime as dt


def no_fall(err_type=IOError, log_path='D:\\simple_test\\log.txt'):
    def decorator(func):
        @ft.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except err_type:
                # print('PROCESS FALLS: ', err_type.__name__)
                with open(log_path, 'a') as f:
                    f.write(str(dt.datetime.now()) + ': {}: PROCESS FALLS: '.format(func.__name__) + str(err_type.__name__) + '\n')
        return wrapper
    return decorator


def logger(log_path='D:\\simple_test\\log.txt', word=''):
    def decorator(func):
        @ft.wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            with open(log_path, 'a') as f:
               f.write( str(dt.datetime.now()) + ': ' + word + ': ' + func.__name__ + ', arguments: ' + str(args) \
                        + ' ' + str(kwargs) + '\n')
        return wrapper
    return decorator


def get_self_dir():
    return os.path.curdir


def revalidate_path(path, recursive=False):
    if not recursive:
        if not os.path.exists(path):
            os.mkdir(path)
            return False
        return True
    else:
        path = path.strip(os.path.sep)
        tmp_path = path.split(os.path.sep)
        pth = tmp_path[0] + os.path.sep
        res = True
        for each in tmp_path[1 :]:
            pth = os.path.join(pth, each)
            if not os.path.exists(pth):
                os.mkdir(pth)
                res = False
        return res


def chek_file(path):
    return os.path.exists(path)


@no_fall(IOError)
def resistant_remove(path):
    os.remove(path)


@no_fall(IOError)
def resistant_rmdir(path):
    os.rmdir(path)


@logger(word='drop file')
def remove(path, ignore_errors):
    if ignore_errors:
        resistant_remove(path)
    else:
        os.remove(path)


@logger(word='drop dir')
def rmdir(path, ignore_errors):
    if ignore_errors:
        resistant_rmdir(path)
    else:
        os.rmdir(path)


def extended_remove(path, recursive=False, ignore_errors=True, save_income_path=True, _seq=0):
    if not recursive:
        if not os.path.exists(path):
            pass
        elif ignore_errors:
            resistant_remove(path)
        else:
            os.remove(path)
    else:
        all_objs = os.listdir(path)
        dirs = list()
        files = list()
        for each in all_objs:
            obj = os.path.join(path, each)
            if os.path.isdir(obj):
                dirs.append(obj)
            else:
                files.append(obj)
        for each in dirs:
            extended_remove(each, recursive, ignore_errors, False, _seq=_seq + 1)
        for each in files:
            remove(each, ignore_errors)
        if not save_income_path or _seq != 0:
            rmdir(path, ignore_errors)
