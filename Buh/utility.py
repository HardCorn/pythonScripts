class BaseError(BaseException):
    """Base class for all errors and exceptions"""
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ': '.join(self.args)


class SingleTonError(BaseError):
    pass


class SequenceError(BaseError):
    pass


class StackError(BaseError):
    pass
    
   
class ListOperationError(BaseError):
    pass


class SingleTon(object):
    """Синглтон с наследованием"""
    instance = {}   # словарь для хранения всех инстансов класса
    init = {}       # словарь для хранения инициализаций

    def __new__(cls, data):
        if cls not in cls.instance:
            cls.instance[cls] = object.__new__(cls)
            cls.init[cls] = False
            # print('new instance', cls.instance)
        return cls.instance[cls]

    def __init__(self, data):
        try:
            if not SingleTon.init[self.__class__]:
                self.data = data
                SingleTon.init[self.__class__] = True
        except:
            raise SingleTonError(f'Unknown error. {self.__class__} has new instance, but not in init dictionary')

    def __getitem__(self, value):
        return self.data[value]

    def __setitem__(self, index, value):
        raise SingleTonError(self.__class__, 'rewrite data', 'You can not rewrite data in static objects.')


class Sequence:         # обычная очередь
    def __init__(self, value=0):
        self.value=value

    def next(self):
        self.value += 1
        return self.value

    def reset(self):
        self.value = 0


class Stack:        # обычный стек, с возможностью работы в режиме очереди
    def __init__(self, data=None, reverse_data=True, queue_mode=False):
        tmp = data or list()
        self.data = tmp
        if reverse_data:
            tmp2 = list()
            while len(tmp) > 0:
                tmp2.append(tmp.pop())
            self.data = tmp2
        self.queue = queue_mode

    def push(self, val):
        self.data.append(val)

    def is_empty(self):
        return len(self.data) > 0

    def pop(self):
        if not self.is_empty():
            if self.queue:
                tmp = self.data[0]
                self.data = self.data[1:]
                return tmp
            else:
                return self.data.pop()
        else:
            raise StackError('Pop error', 'stack is empty!')

    def last(self):
        if not self.is_empty():
            return self.data[len(self.data) - 1]

    def first(self):
        if not self.is_empty():
            return self.data[0]

    def next(self):
        if not self.is_empty():
            return self.pop()