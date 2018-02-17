import os
import datetime as dt
import json as js

"""
    Данные в моделях лежат в текстовых файлах с разделителями и разрешение .data
    Хидеры лежат в отдельных файлах с расширением .header в формате json
    Индексы лежит в файлах .idx в формате json
    Структура Хидера - словарь, содержит: 
        attrs = {порядковый номер в строке файла: {name: имя, type: тип}
        parts = {значения атрибутов партицирования через ";": имя файла} - если одна партиция - main: имя файла
        key = номер ключевого атрибута (или имя)
        index = {имя атрибутов для индекса: имя файла} - пока не планируется создавать
        partitions = {имя атрибута партицирования: формат партицирования} 
            - для дат формат дат, для остальных атрибутов - порядок при склейке, партиции формируются дата+остальный по порядку
"""


DATE_DEFAULT_FMT = 'YYYY-MM-DD'
DAILY_PARTITION_FMT = 'YYYYMMDD'
MONTH_PARTITION_FMT = 'YYYYMM'
YEAR_PARTITION_FMT = 'YYYY'
SHORT_YEAR_PARTITION_FMT = 'YY'
HEADER_EXTENSION = '.header'
DATA_EXTENSION = '.data'
INDEX_EXTENSION = '.idx'


def refmt(fmt):     # приводим к форматам питона, не предполагаем никаких экстравагантных форматов
    return fmt.upper().replace('YYYY', '%Y').replace('YY', '%y').replace('MM', '%m').replace('DD', '%d')


def str_to_date(str, fmt=DATE_DEFAULT_FMT):
    return dt.datetime(str, refmt(fmt)).date()

    
def date_to_str(date, fmt=DATE_DEFAULT_FMT):
    if type(date) != dt.date:
        raise BaseException('Error conversion {0} to str: wrong type({1})'.format(str(date), type(date)))
    return dt.date.strftime(date, refmt(fmt))


def get_date_postfix(date=None, postfix_fmt=MONTH_PARTITION_FMT, date_fmt=DATE_DEFAULT_FMT):
    """
        Формирует постфикс для файлов на основании даты.
        
        по дефолту - сегодняшнее число
        можно так же передавать объекты типа дата и строку с датой 
        (указывая при этом формат, если он отличен от 'YYYY-MM-DD')
    """
    if date is None:
        cur_date = dt.datetime.now()
    elif type(date) in (dt.date, dt.datetime):  
        cur_date = date
    elif type(date) == str and type(date_fmt) == str:
        try:
            cur_date = str_to_date(date, date_fmt)
        except Exception:
            raise ValueError('Can\'t get date from {0} using format {1}'.format(str(date), str(date_fmt)))
    else:
        raise ValueError('Can\'t get postfix using date={0}, fmt={1}'.format(str(date), str(date_fmt)))
    return date_to_str(cur_date, postfix_fmt)
    

def read_model_data(file_path, row_map, delim=';'):
    """
        Генератор, построчно возвращает файл, в виде списков с приведенными типами данных, 
        пустое значение для всех типов кроме строк заменяется на None"""
    with open(file_path, 'r') as f:
        for row in f:
            if not row_map:     # подразумевается что row_map передается извне
                raise BaseException('You can\'t read model data files without it\'s metadata')
            else:
                res_row = []
                tmp_row = row.strip(' \t\n').split(delim)
                if len(tmp_row) > len(row_map):    # row_map не синхронизован со строкой - норма, переписать если короче - нет добавленных атрибутов
                    raise BaseException('Incorrect row \'{0}\' in file {1} (map: {2})'.format(row, file_path, str(row_map)))
                for num in range(len(row_map)):     # пытаемся привести все элементы к типам в соотв с row_map
                    if row_map[num] == 'int':
                        if tmp_row[num] == '':
                            tmp = None
                        else:
                            tmp = int(tmp_row[num])
                    elif row_map[num] == 'str':
                        tmp = tmp_row[num]
                    elif row_map[num] == 'date':
                        if tmp_row[num] == '':
                            tmp = None
                        else:
                            tmp = str_to_date(tmp_row[num])
                    else:       # неизвестный тип данных, поддерживаются только целые числа, даты и строки
                        raise BaseException('Incorrect row map: {}'.format(row_map))
                    res_row.append(tmp)
                yield res_row   # возвращаем полученный набор
    raise StopIteration         # Файл закончился

    
def write_str_to_model_data(file_, row_map, str_, delim=';'):
    if type(file_) == str:  # если вместо файла на вход подали путь к нему
        file_2 = open(file_, 'a')
    else:
        file_2 = file_
    try:        # на случай возникновения каких-либо ошибок
        for num in range(len(str_)):
            if row_map[num] == 'date':
                str_[num] = date_to_str(str_[num])
            else:
                str_[num] = str(str_[num])
        file_2.write(delim.join(str_) + '\n')
    finally:    # сами ошибки не ловим, но обязательно закрываем файл
        if type(file_) == str:
            file_2.close()
    
    
def write_model_data(file_path, list_str, header, delim=';'):
    if not header:
        raise BaseException('Can\'t write data without it\'s header')
    row_map = header
    with open(file_path, 'a') as f:
        for str_ in list_str:
            write_str_to_model_data(f, row_map, str_, delim)
        
 
def replace_model_data(file_path, list_str, header=None, delim=';'):
    try:
        os.remove(file_path)
    except FileNotFoundError:       # если файла не было - фиг с ним
        pass
    write_model_data(file_path, list_str, header, delim)


def drop_model(meta, name):
    file_list = list()                                              # контейнер для файлов
    file_list.append(meta['data_path'] + name + HEADER_EXTENSION)   # кладем header
    for each in meta[name]['index']:
        file_list.append(meta[name]['index'][each])                 # кладем индексы
    parts = meta[name]['parts']
    for each in parts:
        file_list.append(meta['data_path'] + parts[each])           # кладем все файлы партиций в контейнер
    for file in file_list:                                          # удаляем все файлы
        try:
            os.remove(file)
        except FileNotFoundError:
            pass                                                    # возможные ошибки игнорируем
    del meta[name]                                                  # удаляем модель из метаданных


def write_header(meta, name):
    if name not in meta:
        raise ValueError('Model {0} not found in dictionary'.format(name))
    model_dict = meta[name]
    path = meta['data_path'] + name + HEADER_EXTENSION
    # print(model_dict)
    with open(path, 'w') as f:
        js.dump(model_dict, f)


def read_header(meta, name):
    path = meta['data_path'] + name + HEADER_EXTENSION
    with open(path, 'r') as f:
        model_dict = js.load(f)
    attrs = dict()
    for each in model_dict['attrs']:            # json не воспринимает числа как ключ словаря, необходимо переводить вручную
        attrs[int(each)] = model_dict['attrs'][each]
    model_dict['attrs'] = attrs
    meta[name] = model_dict


def get_model_data_name(name, postfix='', extension=DATA_EXTENSION):
    if postfix:
        postfix = '_' + postfix
    return name + postfix + extension
    

class ModelFileWorker:
    """
        model_meta - dictionary
            name - имя модели, к нему привязывается header этой модели
            data_path - путь к файлам модели
    """
    def __init__(self, model_meta=None):
        if model_meta is None:
            self.model_meta = dict()
        else:
            self.model_meta = model_meta
        
    def change_model_header(self, name, header):
        if name not in self.model_meta:
            self.model_meta[name] = dict()
        self.model_meta[name]= header
        write_header(self.model_meta, name)

    def modify_model(self, name, **kwargs):
        if name not in self.model_meta:
            raise ValueError('{0} not found in model metadata'.format(name))
        for each in kwargs:
            self.model_meta[name][each] = kwargs[each]
    
    def del_model(self, name):
        drop_model(self.model_meta, name)
    
    # def add_


if __name__ == '__main__':
    # meta = {'data_path': 'D:\\Users\\HardCorn\\Desktop\\python\\pyCharm\\myScripts\\Buh\\testing_data\\'}
    # meta = {'s': {
    #     'attrs' : {1: {'name': 'd', 'type': 'str'}},
    #     'parts' : {'1;2;3': 's.data'},
    #     'key' : 1,
    #     'index' : {},
    #     'partitions' : {}
    # }, 'data_path': 'D:\\Users\\HardCorn\\Desktop\\python\\pyCharm\\myScripts\\Buh\\testing_data\\'}
    # write_header(meta, 's')
    # read_header(meta, 's')
    # print(meta['s'])
    print(get_model_data_name('n', '200808'))