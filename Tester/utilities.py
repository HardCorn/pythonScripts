class SingleTon(object):

    instance = {}
    init = {}

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
            raise BaseException(f'Unknown error. {self.__class__} has new instance, but not in init dictionary')

    def __getitem__(self, value):
        return self.data[value]

    def __setitem__(self, index, value):
        raise BaseException(self.__class__, 'rewrite data', 'You can not rewrite data in static objects.')


class Sequence:
    def __init__(self, value=0):
        self.value=value

    def next(self):
        self.value += 1
        return self.value
    def reset(self):
        self.value = 0


class BaseError(BaseException):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ': '.join(self.args)


main_sequence = Sequence(0)