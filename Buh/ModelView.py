import modelExceptions as me
from modelFile import ACTUALITY_FIELD_NAME


def check_type(data):
    if isinstance(data, list):
        if not data or isinstance(data[0], list):
            pass
        else:
            raise me.ModelViewException('Check data type', 'Incorrect data type (list of lists expected): list of {}'.format(type(data[0])))
    else:
        raise me.ModelViewException('Check data type', 'Incorrect data type (list of lists expected): {}'.format(type(data)))



class ModelView:
    def __init__(self, name, data, build_view=False, key=None, row_map=None):
        check_type(data)
        self.name = name
        self.data = data
        self.view = False
        self.key = key
        self.row_map = row_map
        if build_view:
            self.convert_to_view()

    def convert_to_view(self):
        if not self.view:
            self.data = self.build_view()
            self.view = True

    def build_view(self):
        key = self.key
        row_map = self.row_map
        if not isinstance(key, int) or not isinstance(row_map, list):
            raise me.ModelViewException(self.name, 'Build View Error', 'Can\'t build view with key = {0} and row_map = {1}'.format(
                key, row_map
            ))
        key = key - 1
        if key not in range(len(row_map)):
            raise me.ModelViewException(self.name, 'Build View Error', 'Incorrect key: {}'.format(key))
        res_dict = dict()
        actuality_dict = dict()
        if ACTUALITY_FIELD_NAME in row_map:
            for num in range(len(row_map)):
                if row_map[num] == ACTUALITY_FIELD_NAME:
                    actuality = num
                    break
        else:
            actuality = -1
        for each in self.data:
            inner_dict = dict()
            if len(row_map) != len(each):
                raise me.ModelViewException(self.name, 'View build Error', 'metadata desync: row: \'{0}\', row_map: \'{1}\''.format(
                                                each, row_map
                                            ))
            for num in range(len(each)):
                if num != key and row_map[num] != ACTUALITY_FIELD_NAME:
                    inner_dict[row_map[num]] = each[num]
            update_flg = True
            if actuality != -1:
                if each[key] in actuality_dict:
                    if actuality_dict[each[key]] <= each[actuality]:
                        update_flg = False
                    else:
                        actuality_dict[each[key]] = each[actuality]
            if update_flg:
                res_dict[each[key]] = inner_dict
        return res_dict

    def __getitem__(self, item):
        if not self.view:
            if not isinstance(item, int):
                raise me.ModelViewException(self.name, 'Get item Error', 'Current instance contains simple data, not a view!',
                                            'Can\'t get item \'{}\''.format(item))
            elif item >= len(self.data):
                raise me.ModelViewException(self.name, 'Get item Error', 'Data index could be only between {0} and {1}, (got {2})'.format(
                    0, len(self.data) - 1, item
                ))
        else:
            if item not in self.data:
                raise me.ModelViewException('Get item Error', self.name, 'Item \'{}\' not found!'.format(
                    item
                ))
        res_tmp = self.data[item]
        res = dict()
        if self.view:
            for each in res_tmp:
                res[each] = res_tmp[each]
            res[self.row_map[self.key - 1]] = item
        else:
            for each in range(len(self.row_map)):
                res[self.row_map[each]] = self.data[item][each]
        return res

    def get_data(self, build_view=False):
        if build_view:
            if self.view:
                return self.data
            else:
                return self.build_view()
        else:
            return self.data


if __name__ == '__main__':
    data = [['a', 1, 4], ['b', 2, 5]]
    a = ModelView('tst_data',data, True, 1, ['name', 'key', 'value'])
    print(a.data, a.view)
    a.convert_to_view()
    print(a['a'])
    dt = a.get_data(False)
    print(dt)
