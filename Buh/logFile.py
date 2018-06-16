import utility as ut


class BaseSingletonTextFile(ut.SingleTon):

    def _init(self, file_path, max_buff=10000):
        self.file = open(file_path, 'a')
        self.buffer=str()
        self.max_buff=max_buff

    # def read(self):
    #     return self.file.read()

    def write(self, string, mode='a'):
        if self.is_closed():
            raise ut.BaseError('File closed!', self.buffer, string)
        if mode == 'w':
            self.file.truncate(0)
            self.file.write(string)
            self.buffer = str()
        elif mode == 'a':
            self.buffer += string
            if len(self.buffer) > self.max_buff:
                self.file.write(self.buffer)
                self.buffer = str()
        else:
            raise ut.BaseError('Incorrect write mode: {}; only \'w\' and \'a\' are allowed'.format(mode))

    def close(self):
        n = self.__class__.decr_init_counter()
        if n < 1:
            self.file.write(self.buffer)
            self.file.close()
            self.buffer = str()

    def is_closed(self):
        return self.file.closed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def get_log_file(log_class, file_path, max_buff=10000):
    f = log_class(file_path, max_buff)
    while True:
        yield f
    # with log_class(file_path, max_buff) as f:
    #     while _val:
    #         yield f


if __name__ == '__main__':
    # f1 = BaseSingletonTextFile(r'D:\simple_test\test_log.log')
    # f2 = BaseSingletonTextFile(r'D:\simple_test\test_log.log')
    # f1.write('fart1\n')
    # f1.close()
    # f2.write('fart2\n')
    # f2.close()
    gen = get_log_file(BaseSingletonTextFile, r'D:\simple_test\test_log.log')
    file1 = next(gen)
    file2 = next(gen)
    with BaseSingletonTextFile(r'D:\simple_test\test_log.log') as nn:
        nn.write('sdfsdfasdf')
    file3 = BaseSingletonTextFile(r'D:\simple_test\test_log.log')
    file1.write('fart11\n')
    file2.write('fart112\n' * 20000)
    print(file1.buffer)
    print(file2.buffer)
    file3.write('i\'m at the end')
    file3.close()
