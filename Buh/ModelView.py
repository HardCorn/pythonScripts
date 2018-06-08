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
    def __init__(self, name, data, build_view=False, key=None, row_map=None, hide=None):
        check_type(data)
        hide = hide or list()
        self.hide = hide
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
        hide = list()
        for each in self.hide:
            hide.append(row_map.index(each))
        if ACTUALITY_FIELD_NAME in row_map:
            actuality = row_map.index(ACTUALITY_FIELD_NAME)
        else:
            actuality = -1
        for each in self.data:
            inner_dict = dict()
            if len(row_map) != len(each):
                raise me.ModelViewException(self.name, 'View build Error', 'metadata desync: row: \'{0}\', row_map: \'{1}\''.format(
                                                each, row_map
                                            ))
            for num in range(len(each)):
                if num != key and num not in hide:
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

    def convert_to_list(self):
        if self.view:
            if not(len(self.hide) == 1 and self.hide[0] == ACTUALITY_FIELD_NAME) and len(self.hide) > 1:
                raise me.ModelViewException('Can\'t rebuild hidden data')
            res_list = list()
            key = self.row_map[self.key - 1]
            for unit in self.data:
                unit_dict = self.data[unit]
                tmp_list = list()
                for each in self.row_map:
                    if each not in (key, ACTUALITY_FIELD_NAME):
                        tmp_list.append(unit_dict[each])
                    elif each == key:
                        tmp_list.append(unit)
                res_list.append(tmp_list)
            self.data = res_list
            self.view = False
        return self.data



if __name__ == '__main__':
    data = [['a', 1, 4], ['b', 2, 5]]
    a = ModelView('tst_data',data, True, 1, ['name', 'key', 'value'])
    print(a.data, a.view)
    a.convert_to_view()
    print(a['a'])
    dt = a.get_data(False)
    print(dt)
    dt2 = a.convert_to_list()
    print(dt2)
