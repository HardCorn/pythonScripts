import os
import datetime as dt
import json as js

"""
    Данные в моделях лежат в текстовых файлах с разделителями и разрешение .data
    Хидеры лежат в отдельных файлах с расширением .header в формате json
    Индексы лежит в файлах .idx в формате json
    Структура Хидера - словарь, содержит: 
        attrs = {порядковый номер в строке файла: {name: имя, type: тип}
        delimiter = строка-разделитель строк в файле
        parts = {значения атрибутов партицирования через ";": имя файла} - если одна партиция - main: имя файла
        key = номер ключевого атрибута (или имя)
        index = {имя атрибутов для индекса: имя файла} - пока не планируется создавать
        partitions = {уровень партицирования: {num: порядок атрибута в файле, fmt: формат партицирования}  
            - для дат формат дат, для остальных атрибутов - None, партиции формируются дата+остальные по уровням
"""

#### Константы ####
DATE_DEFAULT_FMT = 'YYYY-MM-DD'                         # формат по-умолчанию для типа дата
DATETIME_DEFAULT_FMT = 'YYYY-MM-DD HH:MI:SS.SSSSSS'      # формат по-умолчанию для типа дата-время
DAILY_PARTITION_FMT = 'YYYYMMDD'                        # формат дат для ежедневных партиций
MONTH_PARTITION_FMT = 'YYYYMM'                          # формат дат для месячных партиций
YEAR_PARTITION_FMT = 'YYYY'                             # формат для годовых партиций
SHORT_YEAR_PARTITION_FMT = 'YY'                         # короткий формат для годовых партиций
HEADER_EXTENSION = '.header'                            # расширение файлов заголовоков
DATA_EXTENSION = '.data'                                # расширение файлов с данными
# INDEX_EXTENSION = '.idx'                                # расширение файлов с индексами
INTEGER_VALUE = 'int'                                   # значение типа данных в словаре модели (для целых чисел)
STRING_VALUE = 'str'                                    # значение типа данных в словаре модели (для строк)
DATE_VALUE = 'date'                                     # значение типа данных в словаре модели (для дат)
DATETIME_VALUE = 'dttm'                                 # значение типа данных в словаре модели (для типа дата-время)
FLOAT_VALUE = 'float'                                   # значение типа данных в словаре модели (для дробных чисел)
DATA_TYPES_LIST = (INTEGER_VALUE, STRING_VALUE,
                   DATETIME_VALUE, FLOAT_VALUE,
                   DATE_VALUE)                          # список всех доступных типов данных в словаре модели
DATA_PATH = 'data_path'                                 # ключ словаря ModelFileWorker - полный путь к файлам модели
ATTRIBUTE_KEY = 'attrs'                                 # ключ словаря модели - метаданные атрибутов
PARTITION_FILES_KEY = 'parts'                           # ключ словаря модели - метаданные файлов партиций
PK_ATTRIBUTE_KEY = 'key'                                # ключ словаря модели - ключ модели, в разрезе которого строится представление
PARTITION_ATTRIBUTE_KEY = 'partitions'                  # ключ словаря модели - метаданные партиций
# INDEX_FILE_KEY = 'index'                                # ключ словаря модели - метаданные файлов индексов
OPTIONS_KEY = 'options'                                 # ключ словаря модели - кастомные опции представлений
OPTION_HIDE_KEY = 'hide'                                # ключ опций представления - номера атрибутов, скрывающиеся в модели
OPTION_DEFAULT_KEY = 'default'                          # ключ опций представления - значения по-умолчанию
OPTION_LOAD_KEY = 'mode'                                # ключ опций представления - режим записи данных модели
APPEND_MODE = 'a'                                       # режим записи данных - дописать в конец файлов
REPLACE_MODE = 'r'                                      # режим записи данных - полная перегрузка файлов
ACTUALITY_FIELD_NAME = None                             # имя атрибута по которому определяется актуальность ключа
ACTUALITY_FIELD_TYPE = DATETIME_VALUE                   # тип атрибута по которому определяется актуальность ключа
ACTUALITY_DTTM_VALUE = 'current_timestamp'              # значение атрибута актуальности - текущие дата-время
ACTUALITY_DATE_VALUE = 'current_date'                   # значение атрибута актуальности - текущая дата
FILE_DELIMITER_KEY = 'delimiter'                        # ключ словаря модели - разделитель в файлах модели
ATTRIBUTE_NAME_KEY = 'name'                             # ключ словаря атрибутов - имя
ATTRIBUTE_VALUE_KEY = 'value'                           # ключ словаря атрибутов - значение
ATTRIBYTE_TYPE_KEY = 'type'                             # ключ словаря атрибутов - тип данных
PARTITION_FIELD_NUM = 'num'                             # ключ словаря партиций - номер атрибута
PARTITION_FIELD_FORMAT = 'fmt'                          # ключ словаря партиций - формат даты
DEFAULT_SINGLE_PARTITION_VAL = 'main'                   # имя партиции для единственного файла непартицированной таблицы


def quoting(str_):
    if str is not None:
        return '"' + str_ + '"'
    else:
        return ''

        
def dequoting(str_):
    if str_ == '':
        return None
    else:
        if str_[0] == '"' and str_[len(str_) - 1] == '"':
            return str_[1 : len(str_) - 1]
        else:
            return str_


def refmt(fmt):                     # приводим к форматам питона, не предполагаем никаких экстравагантных форматов
    return fmt.upper().replace('YYYY', '%Y').replace('YY', '%y').replace('MM', '%m').replace('DD', '%d').replace(
        'HH', '%H').replace('MI', '%M').replace('SSSSSS', '%f').replace('SS', '%S')


def str_to_datetime(str_, fmt=DATETIME_DEFAULT_FMT):
    if type(str_) == str and str_ == ACTUALITY_DTTM_VALUE:  # проставляем current_timestamp
        str_ = dt.datetime.now().strftime(refmt(fmt))
    return dt.datetime.strptime(str_, refmt(fmt))


def str_to_date(str_, fmt=DATE_DEFAULT_FMT):
    if type(str_) == str and str_ == ACTUALITY_DATE_VALUE:  # проставляем current_date
        str_ = dt.datetime.now().strftime(refmt(fmt))
    return dt.datetime.strptime(str_, refmt(fmt)).date()

    
def datetime_to_str(date, fmt=DATETIME_DEFAULT_FMT):
    if type(date) == str and date == ACTUALITY_DTTM_VALUE:  # проставляем current_timestamp
        date = dt.datetime.now()
    if type(date) != dt.datetime:
        raise BaseException('Error conversion {0} to str: wrong type({1})'.format(str(date), type(date)))
    return dt.datetime.strftime(date, refmt(fmt))


def date_to_str(date, fmt=DATE_DEFAULT_FMT):
    if type(date) == str and date == ACTUALITY_DATE_VALUE:  # проставляем current_date
        date = dt.datetime.now().date()
    if type(date) != dt.date:
        raise BaseException('Error conversion {0} to str: wrong type({1})'.format(str(date), type(date)))
    return dt.date.strftime(date, refmt(fmt))


def get_date_postfix(date=None, postfix_fmt=MONTH_PARTITION_FMT, date_fmt=DATE_DEFAULT_FMT):    # бесполезная вещь, к удалению
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
            cur_date = str_to_datetime(date, date_fmt)
        except Exception:
            raise ValueError('Can\'t get date from {0} using format {1}'.format(str(date), str(date_fmt)))
    else:
        raise ValueError('Can\'t get postfix using date={0}, fmt={1}'.format(str(date), str(date_fmt)))
    if type(cur_date) == date:
        return date_to_str(cur_date, postfix_fmt)
    else:
        return datetime_to_str(cur_date, postfix_fmt)
    

def read_model_data(file_path, row_map, delim=';'):
    """
        Генератор, построчно возвращает файл, в виде списков с приведенными типами данных, 
        пустое значение для всех типов заменяется на None"""
    with open(file_path, 'r') as f:
        for row in f:
            if not row_map:     # подразумевается что row_map передается извне
                raise BaseException('You can\'t read model data files without it\'s metadata')
            else:
                res_row = list()
                tmp_row = row.strip(' \t\n').split(delim)
                if len(tmp_row) > len(row_map):     # row_map не синхронизован со строкой - норма, переписать если короче - нет добавленных атрибутов
                    raise BaseException('Incorrect row \'{0}\' in file {1} (map: {2})'.format(row, file_path, str(row_map)))
                for num in range(len(tmp_row)):     # пытаемся привести все элементы к типам в соотв с row_map
                    if tmp_row[num] == '':
                        tmp = None
                    elif row_map[num] == INTEGER_VALUE:
                        tmp = int(dequoting(tmp_row[num]))
                    elif row_map[num] == STRING_VALUE:
                        tmp = dequoting(tmp_row[num])
                    elif row_map[num] == DATE_VALUE:
                        tmp = str_to_date(dequoting(tmp_row[num]))
                    elif row_map[num] == DATETIME_VALUE:
                        tmp = str_to_datetime(dequoting(tmp_row[num]))
                    elif row_map[num] == FLOAT_VALUE:
                        tmp = float(dequoting(tmp_row[num]))
                    else:       # неизвестный тип данных, поддерживаются только целые числа, даты и строки
                        raise BaseException('Incorrect row map: {}'.format(row_map))
                    res_row.append(tmp)
                diff = len(row_map) - len(tmp_row)  # атрибуты которые есть в метаданных и отсутствуют в строке
                if diff > 0:                        # если они есть
                    for _ in range(diff):           # дописываем None вместо них
                        res_row.append(None)
                yield res_row   # возвращаем полученный набор
    raise StopIteration         # Файл закончился

    
def remap_str(str_, attr_list, file_map, defaults):
    res_str = list(defaults)
    for num in range(len(attr_list)):
        each = attr_list[num]
        if each not in file_map:
            raise ValueError('Error mapping string: attribute \'{}\' not found'.format(each))
        res_str[file_map[each] - 1] = str_[num]
    return res_str


def remap_list(list_str, attr_list, file_map, defaults):
    for num in range(len(list_str)):
        list_str[num] = remap_str(list_str[num], attr_list, file_map, defaults)
    

def str_list_refactor(row_map, str_, attr_list, file_map, defaults, no_remap=False):           # перекодировка строки через row_map
    if not no_remap: # only for check
        str_ = remap_str(str_, attr_list, file_map, defaults)
    for num in range(len(str_)):
        if str_[num] is None:                 # вместо None ставим пустую строку
            str_[num] = ''
        elif row_map[num] == DATE_VALUE:        # даты перекодируем через функцию
            str_[num] = quoting(date_to_str(str_[num]))
        elif row_map[num] == DATETIME_VALUE:    # дату-время также прогоняем через отдельную функцию
            str_[num] = quoting(datetime_to_str(str_[num]))
        else:
            str_[num] = quoting(str(str_[num])) # все остальное перекодируем через конструктор строки
    # diff = len(row_map) - len(str_)             # атрибуты, которые есть в карте, но отсутствуют в строке
    # if diff > 0:
        # for _ in range(diff):
            # str_.append('')                     # дописываем так же как None UPD: здесь лучше попробовать вставить default
    return str_

    
def write_str_to_model_data(file_, row_map, str_, delim, attr_list, file_map, defaults, no_remap):
    if type(file_) == str:  # если вместо файла на вход подали путь к нему
        file_2 = open(file_, 'a')
        try:  # на случай возникновения каких-либо ошибок
            file_2.write(delim.join(str_list_refactor(row_map, str_, attr_list, file_map, defaults, no_remap)) + '\n')
        finally:  # сами ошибки не ловим, но обязательно закрываем файл
            file_2.close()
    else:
        file_.write(delim.join(str_list_refactor(row_map, str_, attr_list, file_map, defaults, no_remap)) + '\n')


def get_model_data_name(name, postfix='', extension=DATA_EXTENSION):
    if postfix:
        postfix = '_' + postfix
    return name + '\\' + name + postfix + extension
    

class ModelFileWorker:
    """ Class for all low-level work with model files
        model_meta - dictionary
            name - имя модели, к нему привязывается header этой модели
            data_path - путь к файлам модели
    """
    def __init__(self, data_path, model_meta=None):
        if model_meta is None:
            self.model_meta = dict()    # создаем с пустым словарем
        else:
            self.model_meta = model_meta
        self.model_meta[DATA_PATH] = data_path
        
    def _get_attr_dict(self, model_name):
        res_dict = self.model_meta[model_name][ATTRIBUTE_KEY]

    def _write_header(self, name):
        if name not in self.model_meta:
            raise ValueError('Model {0} not found in dictionary'.format(name))
        model_dict = self.model_meta[name]
        path = self.model_meta[DATA_PATH] + name + HEADER_EXTENSION
        with open(path, 'w') as f:
            js.dump(model_dict, f)

    def _read_header(self, name):
        path = self.model_meta[DATA_PATH] + name + HEADER_EXTENSION
        with open(path, 'r') as f:
            model_dict = js.load(f)
        attrs = dict()
        partitions = dict()
        for each in model_dict[
            ATTRIBUTE_KEY]:  # json не воспринимает числа как ключ словаря, необходимо переводить вручную
            attrs[int(each)] = model_dict[ATTRIBUTE_KEY][each]
        for each in model_dict[PARTITION_ATTRIBUTE_KEY]:  # тоже самое и с партициями
            partitions[int(each)] = model_dict[PARTITION_ATTRIBUTE_KEY][each]
        model_dict[ATTRIBUTE_KEY] = attrs
        model_dict[PARTITION_ATTRIBUTE_KEY] = partitions
        self.model_meta[name] = model_dict
        
    def _change_header(self, name, header):         # подменяем файл заголовка - потенциально опасно, ломает данные
        if name not in self.model_meta:             # если его не существовало - создаем
            self.model_meta[name] = dict()
        self.model_meta[name]= header
        self._write_header(name)                    # и пишем в файл

    def _modify_header(self, name, **kwargs):            # подменяет кастомные свойства заголовка модели
        if name not in self.model_meta:                  # если модели нет - шлем лесом
            raise ValueError('{0} not found in model metadata'.format(name))
        for each in kwargs:
            self.model_meta[name][each] = kwargs[each]  # ни в коем случае ничего не пишем, после этого обязательно обновлять модель полностью

    def _get_part_name(self, str_, model_name, delim):
        """returns partition name for the PARTITION_FILES_KEY dictionary"""
        part_name = list()                                              # список для склейки через разделитель
        parts_dict = self.model_meta[model_name][PARTITION_ATTRIBUTE_KEY]  # словарь партицирования
        for i in range(len(parts_dict)):                                # забираем все уровни по порядку
            each = i + 1
            num = parts_dict[each][PARTITION_FIELD_NUM]                 # кладем в переменные номер атрибута и его формат
            fmt = parts_dict[each][PARTITION_FIELD_FORMAT]
            if not str_[num - 1] and type(str_[num - 1]) == str:
                part_name.append(str(None))                             # числа/строки
            elif fmt is not None and str_[num - 1] is not None:
                part_name.append(date_to_str(str_[num - 1], fmt))       # с форматом только даты
            else:
                part_name.append(str(str_[num - 1]))
        return delim.join(part_name)                                    # склеиваем разделителем

    def _get_row_map(self, model_name, list_attrs=None):                                 # получаем row_map из заголовка
        """Get row_map from metadata"""
        row_map = list()
        attr_dic = self.model_meta[model_name][ATTRIBUTE_KEY]
        for num in range(len(attr_dic)):
            row_map.append(attr_dic[num + 1][ATTRIBYTE_TYPE_KEY])   # range возвращает знач. от 0 поэтому num + 1
            if list_attrs is not None:
                if attr_dic[num + 1][ATTRIBUTE_NAME_KEY] not in list_attrs:
                    row_map[num - 1] = OPTION_DEFAULT_KEY
        return row_map

    def _validate_partition(self, model_name, partition, delim):
        """
        Function look for partiotion file in metadata and create file if it does not exist
        """
        if partition not in self.model_meta[model_name][PARTITION_FILES_KEY]:
            if partition == DEFAULT_SINGLE_PARTITION_VAL:   # если модель не партицирована
                postfix = ''                                # постфикса нет
            else:
                postfix = partition.replace(delim, '')      # если партицирована удаляем из него символы-разделители
            header = self.model_meta[model_name]
            header[PARTITION_FILES_KEY][partition] = get_model_data_name(model_name, postfix)   # кладем в метаданные
            self._change_header(model_name, header)         # подменяем заголовок

    def _write_model_partition(self, model_name, partition_name, list_str, row_map, delim, mode, file_map, defaults, no_remap):
        """Write data to current partition of model data file"""
        self._validate_partition(model_name, partition_name, delim)
        with open(self.model_meta[DATA_PATH] + self.model_meta[model_name][PARTITION_FILES_KEY][partition_name], mode) as f:
            for str_ in list_str:
                write_str_to_model_data(f, row_map, str_, delim, list_str, file_map, defaults, no_remap)

    def _get_partition_dict(self, list_str, model_name, delim):
        """Create dictionary:
            key - partition name
            value - small list with data only for that partition"""
        part_dict = dict()
        for each in list_str:
            part_name = self._get_part_name(each, model_name, delim)  # для кадой строки считываем ее партицию
            if part_name not in part_dict:                          # если такой еще нет в словаре - добавляем
                part_dict[part_name] = list()
            part_dict[part_name].append(each)                       # дописываем строку
        return part_dict

    def _get_first_n_attrs(self, attr_dict, n=1):
        return list(attr_dict[each + 1][ATTRIBUTE_NAME_KEY] for each in range(n))

    def _check_attr_list(self, model_name, list_str, attr_list, row_map, attr_dict, defaults, file_map):
        sample_str = list_str[0]
        if attr_list is None:
            if len(sample_str) == len(row_map):
                return True
            else:
                return False
        if len(attr_list) != len(sample_str):
            raise ValueError('Error writing data: desync metadata: expected {0} attributes, but {1} attributes found'.format(
                len(attr_list), len(sample_str)
            ))
        for each in attr_list:
            if each not in file_map:
                raise ValueError('Error writing data: attribute \'{0}\' not found in model \'{1}\''.format(
                    each, model_name
                ))
        for num in range(len(attr_dict)):
            if attr_dict[num + 1][ATTRIBUTE_NAME_KEY] != attr_list[num]:
                return False
        return True

    def _get_default_values(self, model_name):
        attr_dict = self.model_meta[model_name][ATTRIBUTE_KEY]
        res_list = list(range(len(attr_dict)))
        for each in range(len(attr_dict)):
            def_ = attr_dict[each + 1][OPTION_DEFAULT_KEY]
            typ_ = attr_dict[each + 1][ATTRIBYTE_TYPE_KEY]
            if typ_ not in (DATETIME_VALUE, DATE_VALUE) \
                or def_ in (ACTUALITY_DTTM_VALUE, ACTUALITY_DATE_VALUE, None):
                res_list[each] = def_
            elif typ_ == DATE_VALUE:
                res_list[each] = str_to_date(def_)
            else:
                res_list[each] = str_to_datetime(def_)
        return res_list

    def write_model_data(self, name: str, list_str: list, attr_list=None, brutal=False):
        """Procedure writes model to data files (and do nothing with it's header)"""
        if len(list_str) == 0:
            raise ValueError('Error writing data: there are no data to write')
        if name not in self.model_meta:             # если к модели еще не обращались - пытаемся прочесть заголовок из файла
            try:
                self._read_header(name)
            except Exception:
                raise BaseException('Can\'t write data without it\'s header')
        row_map = self._get_row_map(name)           # получаем карту строки
        delim = self.model_meta[name][FILE_DELIMITER_KEY]
        attr_dict = self.model_meta[name][ATTRIBUTE_KEY]
        # defaults = list(attr_dict[each + 1][OPTION_DEFAULT_KEY] for each in range(len(attr_dict)))
        defaults = self._get_default_values(name)
        file_map = self.get_file_map(name, header_validation=False)
        no_remap = self._check_attr_list(name, list_str, attr_list, row_map, attr_dict, defaults, file_map)
        if not no_remap:
            if attr_list is None:
                attr_list = self._get_first_n_attrs(attr_dict, len(list_str[0]))
            remap_list(list_str, attr_list, file_map, defaults)
            no_remap = True
        if attr_list is None:
            attr_list = self._get_first_n_attrs(attr_dict, len(list_str[0]))
        if brutal:
            mode = 'w'
        else:
            mode = 'a'
        if not self.model_meta[name][PARTITION_ATTRIBUTE_KEY]: # если нет партиций - пишем в предопределенную партицию DEFAULT_SINGLE_PARTITION_VAL
            self._write_model_partition(name, DEFAULT_SINGLE_PARTITION_VAL, list_str, row_map, delim, mode, file_map, defaults, no_remap)
        else:
            if len(list_str) < 100 and not brutal:                 # если на входе данных мало - пишем их построчно
                for str_ in list_str:
                    part_name = self._get_part_name(str_, name, delim)
                    self._validate_partition(name, part_name, delim)
                    file_path = self.model_meta[DATA_PATH] + self.model_meta[name][PARTITION_FILES_KEY][part_name]
                    write_str_to_model_data(file_path, row_map, str_, delim, attr_list, file_map, defaults, no_remap)
            else:                                                       # если много
                part_dict = self._get_partition_dict(list_str, name, delim)    # сначала бьем данные по партициям
                # del list_str                                          # если после этого изначальные данные не нужны - лучше удалять (память x2)
                # print(part_dict)
                for each in part_dict:                                  # и пишем отдельными партициями по очереди
                    self._write_model_partition(name, each, part_dict[each], row_map, delim, mode, file_map, defaults, no_remap)
                    # del part_dict[each]
    
    def del_model_files(self, name: str):
        """Try to delete all model files
            if all Ok - return True
            if model not found or header is broken return False"""
        if name not in self.model_meta:
            try:
                self._read_header(name)
            except FileNotFoundError:
                return False
        try:
            file_list = list()                                                          # контейнер для файлов
            file_list.append(self.model_meta[DATA_PATH] + name + HEADER_EXTENSION)      # кладем header
            # for each in self.model_meta[name][INDEX_FILE_KEY]:                        # индексов пока нет
            #     file_list.append(self.model_meta[name][INDEX_FILE_KEY][each])         # кладем индексы
            parts = self.model_meta[name][PARTITION_FILES_KEY]
            for each in parts:
                file_list.append(self.model_meta[DATA_PATH] + parts[each])              # кладем все файлы партиций в контейнер
            for file in file_list:                                                      # удаляем все файлы
                try:
                    os.remove(file)
                except FileNotFoundError:
                    pass                                                                # несуществующие файлы игнорируем
            try:
                os.rmdir(self.model_meta[DATA_PATH] + name)
            except FileNotFoundError:
                pass
            del self.model_meta[name]                                                   # удаляем модель из метаданных
            return True
        except Exception:
            return False

    def replace_model_files(self, name: str, list_str: list, header=None):
        """Replace model files using data in memory"""
        if header is None:
            header = self.model_meta[name]                  # сохраняем актуальный заголовок в памяти

        try:
            self._read_header(name)                         # читаем старый заголовок
        except FileNotFoundError:
            pass                                            # если заголовка не было - просто пишем новый
        else:
            self.del_model_files(name)                      # удаляем всю модель
            os.mkdir(self.model_meta[DATA_PATH]+ name)      # создаем директорию для данных
            self._change_header(name, header)               # подменяем заголовок
        self.write_model_data(name, list_str, brutal=True)  # пишем данные с перезаписью на всякий случай

    def _read_partition(self, model_name, part_name=DEFAULT_SINGLE_PARTITION_VAL, sel_attrs=None, file_map=None,
                        filter_=None):
        """read all strings in partition
            filtering structure (not available yet) planning do smth like this:
            {filtering1: {filtering2: {filtering3: {filtering4: True}}, filtering5: True}}"""
        file_path = self.model_meta[DATA_PATH] + self.model_meta[model_name][PARTITION_FILES_KEY][part_name]
        delimiter = self.model_meta[model_name][FILE_DELIMITER_KEY]
        row_map = self._get_row_map(model_name)
        res_list = list()
        if file_map is None and sel_attrs is not None:
            file_map = self.get_file_map(model_name, no_read_header=True)
        for each in read_model_data(file_path, row_map, delimiter):
            if filter_ is not None:
                res_list.append(each)   #здесь еще надо бы фильтровать данные
            else:
                res_list.append(self._get_sel_attrs(each, file_map, sel_attrs))
        return res_list

    def read_model_data(self, name, partitions_=None, read_header=True, ignor_err_partitions=False, filter_=None,
                        selected=None):
        """Read full model or some partition list
            filtering not available yet"""
        if read_header:
            self._read_header(name)
        if name not in self.model_meta:
            raise BaseException('Can\'t read model data without it\'s header!')
        part_list = list()
        if partitions_ is None:         # по умолчанию просто лезем во все партиции модели
            for each in self.model_meta[name][PARTITION_FILES_KEY]:
                part_list.append(each)
        elif type(partitions_) in (list, tuple):    # если передали список или кортеж, пробегаемся по нему
            for each in partitions_:
                if each in self.model_meta[name][PARTITION_FILES_KEY]:
                    part_list.append(each)
                elif not ignor_err_partitions:      # если не выставлен флаг игнорирования кривых партиций и такой партиции нет - падаем
                    raise ValueError('Wrong Partition name \'{0}\' for model \'{1}\''.format(each, name))
        elif type(partitions_) == str:              # если передали строку - считаем что это имя партиции
            if partitions_ in self.model_meta[name][PARTITION_FILES_KEY]:
                part_list.append(partitions_)
            elif not ignor_err_partitions:          # опять падаем если она кривая и нет флага
                raise ValueError('Wrong Partition name \'{0}\' for model \'{1}\''.format(partitions_, name))
        else:
            raise ValueError('Unknown format for partitions_ parameter: only lists, tuples and strings supported')
        result = list()
        file_map = self.get_file_map(name, no_read_header=True)
        for each in part_list:                      # читаем все найденные партиции, если их нет - вернем пустой список
            result += self._read_partition(name, each, filter_=filter_, file_map=file_map, sel_attrs=selected)
        return result   # если не прочли ни одной партиции - на выходе будет пустой список

    def insert_simple_data(self, model, str_, attr_list=None):
        """Will append a single string to a model file"""
        list_str = list()
        list_str.append(str_)
        self.write_model_data(model, list_str, attr_list)

    def _validate_header(self, name, header=None, validation_mode=True, brutal_read=False, no_read=False):
        """Function return model header"""
        if header is None:  # если заголовок не передали - пробуем его прочесть из метаданных или файла
            if name not in self.model_meta or brutal_read:
                if not no_read:
                    try:
                        self._read_header(name)
                    except FileNotFoundError:   # если ни то ни другое не выходит - падаем
                        raise ValueError('Header validation: Unknown model \'{}\''.format(name))
                else:
                    raise ValueError('Header validation: Unknown model \'{}\''.format(name))
            header = self.model_meta[name]
        if validation_mode: # начинаем проверку
            if type(header) != dict:    # заголовок должен быть словарем
                raise TypeError('Header validation: You\'re header is not a dictionary!')
            if (ATTRIBUTE_KEY not in header or PK_ATTRIBUTE_KEY not in header or OPTIONS_KEY not in header\
                    or PARTITION_FILES_KEY not in header or PARTITION_ATTRIBUTE_KEY not in header\
                    or FILE_DELIMITER_KEY not in header):   # проверяем присутствие основных ключей заголовка
                raise KeyError('Header validation: One or more critical parameters not found in header')
            if OPTION_LOAD_KEY not in header[OPTIONS_KEY] \
                or header[OPTIONS_KEY][OPTION_LOAD_KEY] not in (APPEND_MODE, REPLACE_MODE): # проверяем режим загрузки модели
                raise KeyError('Header validation: Correct model loading type not set for the model')
            if type(header[ATTRIBUTE_KEY]) != dict or type(header[PARTITION_FILES_KEY]) != dict\
                    or type(header[PARTITION_ATTRIBUTE_KEY]) != dict or type(header[PK_ATTRIBUTE_KEY]) != int\
                    or type(header[FILE_DELIMITER_KEY]) != str: # проверяем типы основных ключей заголовка
                raise TypeError('Header validation: One or more critical parameter types are incorrect in header')
            for each in header[ATTRIBUTE_KEY]:  # Проверяем словарь атрибутов
                if type(each) != int:           # ключ обязательно int
                    raise TypeError('Header validation: One or more key in attributes dictionary has not supported type ({})'.format(type(each)))
                if type(header[ATTRIBUTE_KEY][each]) != dict:   # соблюдение иерархии
                    raise TypeError('Header validation: One or more critical parameter types are incorect in attributes dictionary')
                if ATTRIBUTE_NAME_KEY not in header[ATTRIBUTE_KEY][each] or OPTION_HIDE_KEY not in header[ATTRIBUTE_KEY][each]\
                        or OPTION_DEFAULT_KEY not in header[ATTRIBUTE_KEY][each]\
                        or ATTRIBYTE_TYPE_KEY not in header[ATTRIBUTE_KEY][each]:   # проверяем присутствие основных параметров атрибута
                    raise KeyError('Header validation: One or more critical parameters not found in attributes dictionary')
                if header[ATTRIBUTE_KEY][each][ATTRIBYTE_TYPE_KEY] not in DATA_TYPES_LIST:  # проверяем типы атрибутов
                    raise ValueError('Header validation: Attribute \'{0}\' has incorrect type \'{1}\''.format(
                        header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY], header[ATTRIBUTE_KEY][each][ATTRIBYTE_TYPE_KEY]
                    ))
            for each in header[PARTITION_ATTRIBUTE_KEY]:    # теперь словарь партиций
                if type(each) != int:           # ключ обязательно int
                    raise TypeError('Header validation: One or more key in partition dictionary has not supported type ({})'.format(type(each)))
                if type(header[PARTITION_ATTRIBUTE_KEY][each]) != dict: # тоже иерархическая структура
                    raise TypeError('Header validation: One or more critical parameter types are incorect in partition dictionary')
                if PARTITION_FIELD_NUM not in header[PARTITION_ATTRIBUTE_KEY][each]\
                        or PARTITION_FIELD_FORMAT not in header[PARTITION_ATTRIBUTE_KEY][each]: # ключевые параметры
                    raise KeyError('Header validation: One or more critical parameters not found in partition dictionary')
            for each in header[PARTITION_FILES_KEY]:    # словарь файлов данных
                if type(each) != str or type(header[PARTITION_FILES_KEY][each]) != str: # все параметры обязательно строковые
                    raise TypeError('Header validation: On or more parameters has incorrect data type in partition files dictionary')
        return header   # возвращаем корректный заголовок

    def _get_atr_num(self, name, atr, header=None):
        """Return place of current attribute in file using it's name
            (you can use other data source - not worker metadata)"""
        header = self._validate_header(name, header, validation_mode=False)    # валидируем header
        for each in header[ATTRIBUTE_KEY]:
            if header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY] == atr:
                return each
        return -1   # возвращаем "-1" если такого атрибута нет

    def get_file_map(self, name, header=None, no_read_header=False, header_validation=True):
        header = self._validate_header(name, header, validation_mode=header_validation, no_read=no_read_header)
        result_map = dict()
        for each in header[ATTRIBUTE_KEY]:
            result_map[header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY]] = each
        return result_map

    def add_attribute(self, model_name, attribute_name, attribute_type, **kwargs):
        header = self._validate_header(model_name)
        if attribute_type not in DATA_TYPES_LIST:   # проверяем валидность типа
            raise ValueError('Unknown data type \'{0}\' for attribute {1}'.format(attribute_type, attribute_name))
        for each in header[ATTRIBUTE_KEY]:          # проверяем модель на существование добавляемого атрибута
            if header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY] == attribute_name:
                raise ValueError('{0} already exist in model {1}'.format(attribute_name, model_name))
        num = len(header[ATTRIBUTE_KEY]) + 1        # номер нового атрибута
        header[ATTRIBUTE_KEY][num] = dict()         # дописываем в заголовок новый атрибут
        header[ATTRIBUTE_KEY][num][ATTRIBUTE_NAME_KEY] = attribute_name
        header[ATTRIBUTE_KEY][num][ATTRIBYTE_TYPE_KEY] = attribute_type
        header[ATTRIBUTE_KEY][num][OPTION_DEFAULT_KEY] = None   # кастомные опции будут дописаны позже ставим умолчания
        header[ATTRIBUTE_KEY][num][OPTION_HIDE_KEY] = False
        for each in kwargs:                                     # проставляем custom опции атрибутов
            if each == OPTION_DEFAULT_KEY:
                if attribute_type in (DATE_VALUE, DATETIME_VALUE) and kwargs[each] not in (ACTUALITY_DATE_VALUE, ACTUALITY_DTTM_VALUE):
                    if attribute_type == DATE_VALUE:
                        header[ATTRIBUTE_KEY][num][each] = date_to_str(kwargs[each])
                    if attribute_type == DATETIME_VALUE:
                        header[ATTRIBUTE_KEY][num][each] = datetime_to_str(kwargs[each])
                else:
                    header[ATTRIBUTE_KEY][num][each] = kwargs[each]
            else:
                header[ATTRIBUTE_KEY][num][each] = kwargs[each]
        self._validate_header(model_name, header, no_read=True) # проверяем новый заголовок
        self._change_header(model_name, header)                 # и подменяем его

    def rename_attribute(self, model_name, old_name, new_name):     # переименовывает атрибут (переписывает заголовок)
        header = self._validate_header(model_name, validation_mode=False)
        num = self._get_atr_num(model_name, old_name, header)       # ищем старое имя атрибута
        num_new = self._get_atr_num(model_name, new_name, header)   # ищем новое имя
        if num == -1:                                               # если не нашли старое - падаем
            raise ValueError('Error renaming attributes: model {0} hasn\'t attribute {1}'.format(model_name, old_name))
        elif num_new != -1:                                         # если нашли новое - падаем
            raise ValueError('Error renaming attributes: model {0} already has attribute {1}'.format(model_name, new_name))
        header[ATTRIBUTE_KEY][num][ATTRIBUTE_NAME_KEY] = new_name   # меняем имя в заголовке
        self._validate_header(model_name, header, validation_mode=True, no_read=True) # проверяем заголовок
        self._change_header(model_name, header)                     # подменяем заголовок

    def _get_sel_attrs(self, str_, file_map, new_map=None):         # функция для реализации выборки конкретных атрибутов из строки в нужном порядке
        if new_map is None:                                         # если не передали список с атрибутами - возвращаем строку
            return str_
        # result_map = list()
        res_str = list()    
        for each in new_map:
            if each not in file_map:                                # если в списке атрибутов есть "лишний" - падаем
                raise ValueError('Error selecting: Unknown attribute {0}'.format(str(each)))
            res_str.append(str_[file_map[each] - 1])                # если все ок, добавляем индекс атрибута в результирующий список
        # for each in result_map:
        #     res_str.append(str_[each - 1])                          # собираем по индексам 
        return res_str

    def delete_attribute(self, model_name, attr_name, new_key_attr=None):           # удаление атрибута модели
        header = self._validate_header(model_name, validation_mode=False)
        num = self._get_atr_num(model_name, attr_name, header)
        new_key = -1
        if new_key_attr is not None:                                                # обрабатываем возможное удаление ключа модели
            new_key = self._get_atr_num(model_name, new_key_attr, header)
        part_level = -1
        if num == -1:                                                               # падаем на удалении несуществующего
            raise ValueError('Error deleting attributes: model {0} hasn\'t attribute {1}'.format(model_name, attr_name))
        for each in header[PARTITION_ATTRIBUTE_KEY]:                                # обрабатываем возможное вхождение в партиции
            if header[PARTITION_ATTRIBUTE_KEY][each][PARTITION_FIELD_NUM] == num:
                part_level = each
        if header[PK_ATTRIBUTE_KEY] == num:
            if new_key == -1:                                                       # если действительно удаляем ключ, а нового нет - падаем
                raise ValueError('Error deleting attributes: delete key attribute with no new key attribute selected')
            header[PK_ATTRIBUTE_KEY] = new_key
        if part_level != -1:                                                        # обрабатываем удаление атрибута партицирования
            max_lvl = len(header[PARTITION_ATTRIBUTE_KEY])
            header[PARTITION_ATTRIBUTE_KEY][part_level] = header[PARTITION_ATTRIBUTE_KEY][max_lvl]  # меняем удаляемый уровень партиции максимальным
            del header[PARTITION_ATTRIBUTE_KEY][max_lvl]                            # и удаляем максимальный уровень
            header[PARTITION_FILES_KEY] = dict()                                    # сносим словарь файлов партиций - более не валиден
        max_atr = len(header[ATTRIBUTE_KEY])                                        # аналогично партициям обрабатываем удаление самого атрибута
        header[ATTRIBUTE_KEY][num] = header[ATTRIBUTE_KEY][max_atr]
        del header[ATTRIBUTE_KEY][max_atr]
        new_map = self.get_file_map(model_name, header, no_read_header=True)        # получаем новую карту файла (поменялся порядок атрибутов и их число)
        new_data = self.read_model_data(model_name, selected=new_map)               # читаем данные модели используя новую карту файла
        self.replace_model_files(model_name, new_data, header)                      # переписываем все файлы модели

    def create_model(self, name, attrs, key, partition=None, delim=';', defaults=None, hide=None, load_mode=APPEND_MODE):
        """Function create new model:
            name - new model name
            attrs - dictionary with model attributes: {name1: type1, name2: type2, ...}
            key - prime key attribute (used for building a view)
            defaults - dictionary {name1: default value1, name2: default value2, ...}
            hide - string or list of strings - this attributes wouldn't be shown in model view
            load_mode - model loading mode: 'a' - append new data, 'r' - full replace model data
            delim - model files delimiter
            partition - dictionary with model partition fields: {name1: format1, ...}
                any formats for non-dates attributes will be ignored, and may contains comments, for example,
                for dates you should write python-style formats or YYYYMMDD with any delimiters
                (except delimiter of model file of course)"""
        try:    # Проверяем модель на предмет существования пробуем прочитать
            self._read_header(name) # пробуем прочитать ее header
        except Exception:
            pass    # игнорируя все ошибки
        if name in self.model_meta:     # и падаем если нам это удается
            raise ValueError('Model called \'{0}\' already exists: {1}'.format(name, str(self.model_meta[name])))
        header = dict()
        header[ATTRIBUTE_KEY] = dict()
        header[PARTITION_FILES_KEY] = dict()
        iter = 1    # итератор ключей словаря атрибутов
        pk_idx = -1 # индекс ключевого атрибута
        for each in attrs:
            if attrs[each] is None:
                raise ValueError('Attribute name cannot be None!')
            header[ATTRIBUTE_KEY][iter] = dict()
            header[ATTRIBUTE_KEY][iter][ATTRIBUTE_NAME_KEY] = each
            header[ATTRIBUTE_KEY][iter][ATTRIBYTE_TYPE_KEY] = attrs[each]
            if each == key:
                pk_idx = iter   # если находим ключ сохраняем его индекс
            iter += 1
        if pk_idx == -1:    # если не нашли - падаем
            raise KeyError('You Can\'t create model without key: there are no attribute '
                           'called \'{0}\' in {1}'.format(key, str(attrs)))
        header[PK_ATTRIBUTE_KEY] = pk_idx
        parts = dict()  # словарь для данных о партицировании
        header[PARTITION_ATTRIBUTE_KEY] = parts
        if partition is not None:
            iter = 1    # вновь задаем итератор для создания уровней партицирования
            for each in partition:
                header[PARTITION_ATTRIBUTE_KEY][iter] = dict()
                num = self._get_atr_num(name, each, header)
                if num == -1:   # падаем если не нашли атрибута с переданным именем
                    raise KeyError('Error model creating: There are no {0} attribute, can\'t create partition'.format(each))
                header[PARTITION_ATTRIBUTE_KEY][iter][PARTITION_FIELD_NUM] = num
                header[PARTITION_ATTRIBUTE_KEY][iter][PARTITION_FIELD_FORMAT] = partition[each]
                iter += 1
        header[FILE_DELIMITER_KEY] = delim  # не забываем задать разделитель (по умолчанию ";")
        header[OPTIONS_KEY] = dict()    # словарь опций представления модели
        if load_mode == APPEND_MODE:    # загрузка модели добавлением новой порции данных
            header[OPTIONS_KEY][OPTION_LOAD_KEY] = APPEND_MODE                      # пишем метод загрузки
            num = len(header[ATTRIBUTE_KEY]) + 1
            header[ATTRIBUTE_KEY][num] = dict()                                     # добавляем "атрибут актуальности"
            header[ATTRIBUTE_KEY][num][ATTRIBUTE_NAME_KEY] = ACTUALITY_FIELD_NAME   # имя None
            header[ATTRIBUTE_KEY][num][ATTRIBYTE_TYPE_KEY] = ACTUALITY_FIELD_TYPE   # тип дата-время
            if hide is None:                                                        # маскируем его в представлении
                hide = list()
                hide.append(ACTUALITY_FIELD_NAME)
            elif type(hide) == list:
                hide.append(ACTUALITY_FIELD_NAME)
            elif type(hide) == str:
                hide = list(hide)
                hide.append(ACTUALITY_FIELD_NAME)
            else:
                raise ValueError('Error model creation: Unknown type for \'hide\' parameter! Use list or string!')
            if defaults is None:                                                    # выставляем значение по-умолчанию
                defaults = dict()
            defaults[ACTUALITY_FIELD_NAME] = ACTUALITY_DTTM_VALUE
        elif load_mode == REPLACE_MODE:                                             # метод полной перезаписи модели
            header[OPTIONS_KEY][OPTION_LOAD_KEY] = REPLACE_MODE
        else:                                                                       # других пока не предусмотрено
            raise ValueError('Error model creation: Loading mode could be only {0} or {1}'.format(APPEND_MODE, REPLACE_MODE))
        if type(hide) not in (list, str, type(None)):
            raise ValueError('Error model creation: Unknown type for \'hide\' parameter! Use list or string!')
        if type(defaults) not in (dict, type(None)):
            raise ValueError('Error model creation: Unknown type for \'default\' parameter! Use dictionary!')
        for each in header[ATTRIBUTE_KEY]:                                          # проставим опции атрибутов для представлений
            attr_name = header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY]
            attr_type = header[ATTRIBUTE_KEY][each][ATTRIBYTE_TYPE_KEY]
            if (type(defaults) == dict and attr_name in defaults):                  # значения по умолчанию
                if attr_type == DATE_VALUE and defaults[attr_name] != ACTUALITY_DATE_VALUE:
                    if type(defaults[attr_name]) == str:
                        str_to_date(defaults[attr_name])
                        def_ = defaults[attr_name]
                    else:
                        def_ = date_to_str(defaults[attr_name])
                elif attr_type == DATETIME_VALUE and defaults[attr_name] != ACTUALITY_DTTM_VALUE:
                    if type(defaults[attr_name]) == str:
                        str_to_datetime(defaults[attr_name])
                        def_ = defaults[attr_name]
                    else:
                        def_ = datetime_to_str(defaults[attr_name])
                else:
                    def_ = defaults[attr_name]
            else:
                def_ = None
            if (type(hide) == str and attr_name == hide) \
                    or (type(hide) == list and attr_name in hide):                  # скроем ненужные
                hd_ = True
            else:
                hd_ = False
            header[ATTRIBUTE_KEY][each][OPTION_DEFAULT_KEY] = def_
            header[ATTRIBUTE_KEY][each][OPTION_HIDE_KEY] = hd_
        os.mkdir(self.model_meta[DATA_PATH] + name)                                 # создадим директорию для файлов данных
        self._validate_header(name, header, validation_mode=True, no_read=True) # Проверим созданный заголовок
        self._change_header(name, header)   # и в конце заводим заголовок в метаданные и пишем его файл
        del self.model_meta[name]           # Параметрами передаются списки и словари. на всякий случай рвем связь с метаданными

    def get_model_header(self, model_name): # просто читаем и отдаем заголовок
        self._read_header(model_name)
        return self.model_meta[model_name]

    def modify_partition(self, model_name, modif_type, attr_name, attr_fmt=None):   # модифицирует словарь партиций вынести эту функцию в fileworker'a в модель
        if modif_type not in ('add', 'remove', 'reformat'):                         # неизвестные типы модификаций
            raise ValueError('Error modifying partitioning for {0}: unknown modification type \'{1}\''.format(
                model_name, modif_type
            ))
        header = self._validate_header(model_name, validation_mode=False)           # читаем заголовок
        num = self._get_atr_num(model_name, attr_name, header)
        if num == -1:                                                               # атрибут отсутствует в модели
            raise ValueError('Error modifying partitioning for {0}: Unknown attribute \'{1}\''.format(
                model_name, attr_name
            ))
        attr_type = header[ATTRIBUTE_KEY][num][ATTRIBYTE_TYPE_KEY]                  # сохраняем тип атрибута
        if attr_type in (DATE_VALUE, DATETIME_VALUE) and modif_type in ('add', 'reformat'): # проверяем форма для дат при смене формата/добавлении партиции
            try:
                datetime_to_str(dt.datetime.now(), attr_fmt)
            except Exception:
                raise ValueError('Error modifying partitioning for {0}: Incorrect format {1} for date or datetime'.format(
                    model_name, attr_fmt
                ))
        if modif_type == 'add':                                                     # добавление
            for each in header[PARTITION_ATTRIBUTE_KEY]:
                if header[PARTITION_ATTRIBUTE_KEY][each][PARTITION_FIELD_NUM] == num:   # проверка на то что партицирование по этому атрибуту уже есть
                    raise KeyError('Error modifying partitioning for {0}: model already partitioned by {1}'.format(
                        model_name, attr_name
                    ))
            new_part = len(header[PARTITION_ATTRIBUTE_KEY]) + 1                     # добавляем новый уровень в словарь партиций
            header[PARTITION_ATTRIBUTE_KEY][new_part] = dict()
            header[PARTITION_ATTRIBUTE_KEY][new_part][PARTITION_FIELD_NUM] = num
            header[PARTITION_ATTRIBUTE_KEY][new_part][PARTITION_FIELD_FORMAT] = attr_fmt
        else:
            mod_part = -1                                                           # найдем атрибут в словаре партиций
            for each in header[PARTITION_ATTRIBUTE_KEY]:
                if header[PARTITION_ATTRIBUTE_KEY][each][PARTITION_FIELD_NUM] == num:
                    mod_part = each
            if mod_part == -1:                                                      # если его нет - падаем
                raise KeyError('Error modifying partitioning for {0}: model don\'t partitioned by {1}'.format(
                    model_name, attr_name
                ))
            if modif_type == 'reformat':                                            # если цель - смена формата - меняем значение соотв. ключа в словаре
                header[PARTITION_ATTRIBUTE_KEY][mod_part][PARTITION_FIELD_FORMAT] = attr_fmt
                if attr_type not in (DATETIME_VALUE, DATE_VALUE):
                    return True     # Костыль. Если меняем формат для не даты - возвращаем True, дальше ничего делать не надо
            else:
                max_part = len(header[PARTITION_ATTRIBUTE_KEY])                     # при удалении - меняем удаляемый атрибут с последним и удаляем последний
                header[PARTITION_ATTRIBUTE_KEY][mod_part] = header[PARTITION_ATTRIBUTE_KEY][max_part]
                del header[PARTITION_ATTRIBUTE_KEY][max_part]
        header[PARTITION_FILES_KEY] = dict()                # сносим невалидный словарь файлов модели
        # new_map = self.get_file_map(model_name, header, no_read_header=True)      # получаем словарь новых атрибутов (зачем?!)
        # data = self.read_model_data(model_name, selected=new_map)                   
        data = self.read_model_data(model_name)                                     # читаем файлы модели
        self.replace_model_files(model_name, data, header)                          # переписываем файлы используя прочтенные данные


if __name__ == '__main__':
    pass
    # meta = {DATA_PATH: 'D:\\Users\\HardCorn\\Desktop\\python\\pyCharm\\myScripts\\Buh\\testing_data\\'}
    # meta = {'s': {
    #     ATTRIBUTE_KEY : {1: {ATTRIBUTE_NAME_KEY: 'd', ATTRIBYTE_TYPE_KEY: STRING_VALUE}},
    #     PARTITION_FILES_KEY : {'1;2;3': 's.data'},
    #     PK_ATTRIBUTE_KEY : 1,
    #     INDEX_FILE_KEY : {},
    #     PARTITION_ATTRIBUTE_KEY : {}
    # }, DATA_PATH: 'D:\\Users\\HardCorn\\Desktop\\python\\pyCharm\\myScripts\\Buh\\testing_data\\'}
    # write_header(meta, 's')
    # read_header(meta, 's')
    # print(meta['s'])
    a = ModelFileWorker('D:\\Users\\HardCorn\\Desktop\\python\\pyCharm\\myScripts\\Buh\\testing_data\\')
    print(a.del_model_files('New_model'))
    attrs_dict = {'key_field': 'str',
                  'info_field1': 'str',
                  'info_field2': 'int',
                  'date_field': 'date'}
    defaults_dict = {'key_field': 'no_sense_string',
                     'info_field1': 'i\'m a monkey',
                     'info_field2': 42,
                     'date_field': dt.date(2015,12,29)}
    partition_dict = {'date_field': 'YYYYMM',
                      'info_field2': None}
    a.create_model('New_model', attrs_dict, 'key_field', partition_dict, delim='|^|', defaults=defaults_dict)
    a.insert_simple_data('New_model', ['k1', 'i1', 3, dt.date(2018,1,1)])
    a.insert_simple_data('New_model', ['k1', 'i1', 3, dt.date(2018, 2, 1)])
    a.write_model_data('New_model', [['k2', 'i1', 3, dt.date(2018,1,2)],['k1', 'i1', 4, dt.date(2018,1,3)]])
    a.add_attribute('New_model', 'info_field3', 'float', default=3.14)
    a.add_attribute('New_model', 'info_field4', 'dttm', default=dt.datetime(1,1,1))
    a.rename_attribute('New_model', 'info_field3', 'floating_data')
    a.delete_attribute('New_model', 'info_field2')
    a.insert_simple_data('New_model', ['k5', 'i10', dt.datetime(2000,11,10,5,30), None, ACTUALITY_DTTM_VALUE, 3.5])
    a.insert_simple_data('New_model', ['k5', 'i10', dt.datetime(2000, 11, 10, 5, 30), dt.date(2018, 4, 1), ACTUALITY_DTTM_VALUE, 321365654438433452456475864674.5123456789])
    a.insert_simple_data('New_model', ['k6', dt.date(2017,5,14)], ['key_field', 'date_field'])
    a.modify_partition('New_model', 'remove', 'date_field')
    a.modify_partition('New_model', 'add', 'date_field', 'YYYYMMDD')
    a.modify_partition('New_model', 'reformat', 'date_field','YYYYMM')
    sel = ['date_field', 'floating_data', 'key_field']
    print(a.read_model_data('New_model', selected=sel))
    print(a.read_model_data('New_model'))
    print(a.get_file_map('New_model'))
    print(a._get_row_map('New_model'))
    # print(datetime_to_str(dt.datetime(2017,8,5,4,12,33,55)))
    # c = str_to_datetime('2017-08-05 04:12:33.000055')
    # print(get_date_postfix('2017-08-05 04:12:33.000055', date_fmt=DATETIME_DEFAULT_FMT))
    # print(get_model_data_ name('n', DEFAULT_SINGLE_PARTITION_VAL))

    # 'default'