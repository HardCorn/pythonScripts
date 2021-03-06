import modelExceptions as me
from modelFile import ACTUALITY_FIELD_NAME
import modelUtility as mu


def check_type(data):
    if isinstance(data, list):
        if not data or isinstance(data[0], list):
            pass
        else:
            raise me.ModelViewException('Check data type', 'Incorrect data type (list of lists expected): list of {}'.format(type(data[0])))
    else:
        raise me.ModelViewException('Check data type', 'Incorrect data type (list of lists expected): {}'.format(type(data)))



class ModelView:
    def __init__(self, name, data, log_generator, build_view=False, key=None, row_map=None, hide=None, filter_list=True):
        check_type(data)
        hide = hide or list()
        self.logger = mu.Logger('ModelView', log_generator)
        self.logger.note('__init__', 'start')
        self.hide = hide
        self.name = name
        self.data = data
        self.view = False
        self.key = key
        self.row_map = row_map
        if build_view:
            self.convert_to_view()
        elif filter_list:
            self.filter_list()
        self.logger.note('__init__', 'ended successfully')

    log_func = mu.Decor._logger

    @log_func()
    def filter_list(self):
        if ACTUALITY_FIELD_NAME not in self.row_map:
            pass
        else:
            act_num = self.row_map.index(ACTUALITY_FIELD_NAME)
            key = self.key

            def sort_key(input_data):
                return str(input_data[key]) + '|^|' + str(input_data[act_num])

            self.data.sort(key=sort_key, reverse=True)
            prev_val = None
            res_list = list()
            for each in self.data:
                if prev_val != each[key]:
                    res_list.append(each)
                    prev_val = each[key]
            self.data = res_list

    @log_func()
    def convert_to_view(self):
        if not self.view:
            self.data = self.build_view()
            self.view = True

    @log_func()
    def build_view(self):
        key = self.key
        row_map = self.row_map
        if not isinstance(key, int) or not isinstance(row_map, list):
            self.logger.error('buid_view', 'Can\'t build view with key = {0} and row_map = {1}'.format(
                key, row_map
            ), me.ModelViewException)
            # raise me.ModelViewException(self.name, 'Build View Error', 'Can\'t build view with key = {0} and row_map = {1}'.format(
            #     key, row_map
            # ))
        key = key - 1
        if key not in range(len(row_map)):
            self.logger.error('build_view', 'Incorrect key: {}'.format(key), me.ModelViewException)
            # raise me.ModelViewException(self.name, 'Build View Error', 'Incorrect key: {}'.format(key))
        res_dict = dict()
        actuality_dict = dict()
        hide = list()
        for each in self.hide:
            hide.append(row_map.index(each))
        if ACTUALITY_FIELD_NAME in row_map:
            actuality = row_map.index(ACTUALITY_FIELD_NAME)
        else:
            actuality = -1
        self.logger.debug('build_view', _name=self.name, key=key, row_map=row_map, hide=hide)
        for each in self.data:
            inner_dict = dict()
            if len(row_map) != len(each):
                self.logger.error('build_view', 'metadata desync: row: \'{0}\', row_map: \'{1}\''.format(
                                                each, row_map
                                            ), me.ModelViewException)
                # raise me.ModelViewException(self.name, 'View build Error', 'metadata desync: row: \'{0}\', row_map: \'{1}\''.format(
                #                                 each, row_map
                #                             ))
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

    @log_func()
    def __getitem__(self, item):
        self.logger.debug('__getitem__', _name=self.name, view=self.view, item=item)
        if not self.view:
            if not isinstance(item, int):
                self.logger.error('__getitem__', 'Current instance contains simple data, not a view!' +
                                            'Can\'t get item \'{}\''.format(item), me.ModelViewException)
                # raise me.ModelViewException(self.name, 'Get item Error', 'Current instance contains simple data, not a view!',
                #                             'Can\'t get item \'{}\''.format(item))
            elif item >= len(self.data):
                self.logger.error('__getitem__', 'Data index could be only between {0} and {1}, (got {2})'.format(
                    0, len(self.data) - 1, item
                ), me.ModelViewException)
                # raise me.ModelViewException(self.name, 'Get item Error', 'Data index could be only between {0} and {1}, (got {2})'.format(
                #     0, len(self.data) - 1, item
                # ))
        else:
            if item not in self.data:
                self.logger.error('__getitem__', 'Item \'{}\' not found!'.format(
                    item
                ), me.ModelViewException)
                # raise me.ModelViewException('Get item Error', self.name, 'Item \'{}\' not found!'.format(
                #     item
                # ))
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

    @log_func()
    def get_data(self, build_view=False):
        if build_view:
            if self.view:
                return self.data
            else:
                return self.build_view()
        else:
            return self.data

    @log_func()
    def convert_to_list(self):
        self.logger.debug('convert_to_list', _name=self.name, view=self.view, hide=self.hide, row_map=self.row_map)
        if self.view:
            if not(len(self.hide) == 1 and self.hide[0] == ACTUALITY_FIELD_NAME) and len(self.hide) > 1:
                self.logger.error('convert_to_list', 'Can\'t rebuild hidden data', me.ModelViewException)
                # raise me.ModelViewException('Can\'t rebuild hidden data')
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
