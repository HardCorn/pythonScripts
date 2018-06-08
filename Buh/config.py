import os
import smartSplit as ss


class Config:
    def __init__(self, file_path, auto_save=True):
        self.file_path = file_path
        self.auto_save = auto_save
        self._data = self.read()

    def read(self):
        res = dict()
        try:
            for each in open(self.file_path, 'r'):
                tmp = each.strip()
                tmp = tmp.partition('=')
                res[tmp[0]] = ss.str_to_type(tmp[2], inner_quotes=False)
        except IOError:
            pass
        return res

    def __getitem__(self, item):
        if item in self._data:
            return self._data[item]
        else:
            return None

    def __setitem__(self, key, value):
        self._data[key] = value
        if self.auto_save:
            self.save()

    def save(self):
        tmp_str = str()
        for each in self._data:
            tmp_str += str(each) + '=' + str(self._data[each]) + '\n'
        with open(self.file_path + 'diff', 'w') as f:
            f.write(tmp_str)
        try:
            os.remove(self.file_path)
        except IOError:
            pass
        os.rename(self.file_path + 'diff', self.file_path)

    def __iter__(self):
        tmp = list(self._data.keys())
        for each in tmp:
            yield each
        raise StopIteration()

    def __len__(self):
        return len(self._data)


if __name__ == '__main__':
    b = Config('sample_config.conf')
    b['simple_key'] = 'simple_value'
    b['bool'] = False
    b['int'] = 1000
    b['float'] = 23235.4
    b.read()
    for each in b:
        print(each, '=', b[each], type(b[each]))
