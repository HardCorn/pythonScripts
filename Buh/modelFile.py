import os
import dates as dt
import json as js
import modelExceptions as er
import modelUtility as mu
import osExtension as oe

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
DEBUG = True
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


# def get_date_postfix(date=None, postfix_fmt=dt.MONTH_PARTITION_FMT, date_fmt=dt.DATE_DEFAULT_FMT):    # бесполезная вещь, к удалению
#     """
#         Формирует постфикс для файлов на основании даты.
#
#         по дефолту - сегодняшнее число
#         можно так же передавать объекты типа дата и строку с датой
#         (указывая при этом формат, если он отличен от 'YYYY-MM-DD')
#     """
#     if date is None:
#         cur_date = dt.datetime.now()
#     elif type(date) in (dt.date, dt.datetime):
#         cur_date = date
#     elif type(date) == str and type(date_fmt) == str:
#         try:
#             cur_date = dt.str_to_datetime(date, date_fmt)
#         except Exception:
#             raise er.UtilityException('Can\'t get date from {0} using format {1}'.format(str(date), str(date_fmt)))
#     else:
#         raise er.UtilityException('Can\'t get postfix using date={0}, fmt={1}'.format(str(date), str(date_fmt)))
#     if type(cur_date) == date:
#         return dt.date_to_str(cur_date, postfix_fmt)
#     else:
#         return dt.datetime_to_str(cur_date, postfix_fmt)


def read_str(logger : mu.Logger, row, row_map, delim, file_path=None, part_read=False, part_fmt=None):
    res_row = list()
    tmp_row = row.strip(' \t\n').split(delim)
    if len(tmp_row) > len(row_map):     # row_map не синхронизован со строкой - норма, переписать если короче - нет добавленных атрибутов
        logger.error('read_str{outer function}', 'Incorrect row \'{0}\' in file {1} (map: {2})'.format(row, file_path, str(row_map)), er.ModelReadError)
        # raise er.ModelReadError('Incorrect row \'{0}\' in file {1} (map: {2})'.format(row, file_path, str(row_map)))
    for num in range(len(tmp_row)):     # пытаемся привести все элементы к типам в соотв с row_map
        if tmp_row[num] == '':
            tmp = None
        elif part_read and tmp_row[num] == 'None':
            tmp = None
        elif row_map[num] == INTEGER_VALUE:
            tmp = int(dequoting(tmp_row[num]))
        elif row_map[num] == STRING_VALUE:
            tmp = dequoting(tmp_row[num])
        elif row_map[num] == DATE_VALUE:
            if not part_read:
                tmp = dt.str_to_date(dequoting(tmp_row[num]))
            else:
                try:
                    tmp = dt.dateRange(dequoting(tmp_row[num]), part_fmt)
                except dt.dateRange.StopRange:
                    tmp = dt.str_to_date(dequoting(tmp_row[num]))
        elif row_map[num] == DATETIME_VALUE:
            if not part_read:
                tmp = dt.str_to_datetime(dequoting(tmp_row[num]))
            else:
                try:
                    tmp = dt.dateRange(dequoting(tmp_row[num]), part_fmt)
                except dt.dateRange.StopRange:
                    tmp = dt.str_to_datetime(dequoting(tmp_row[num]))
        elif row_map[num] == FLOAT_VALUE:
            tmp = float(dequoting(tmp_row[num]))
        else:       # неизвестный тип данных, поддерживаются только целые числа, даты и строки
            logger.error('read_str{outer function}', 'Incorrect row map: {}'.format(row_map), er.ModelReadError)
            # raise er.ModelReadError('Incorrect row map: {}'.format(row_map))
        res_row.append(tmp)
    diff = len(row_map) - len(tmp_row)  # атрибуты которые есть в метаданных и отсутствуют в строке
    if diff > 0:                        # если они есть
        for _ in range(diff):           # дописываем None вместо них
            res_row.append(None)
    return res_row


def read_model_data(logger : mu.Logger, file_path, row_map, delim=';'):
    """
        Генератор, построчно возвращает файл, в виде списков с приведенными типами данных, 
        пустое значение для всех типов заменяется на None"""
    with open(file_path, 'r') as f:
        for row in f:
            if not row_map:     # подразумевается что row_map передается извне
                logger.error('_read_partition', 'You can\'t read model data files without it\'s metadata', er.ModelReadError)
                # raise er.ModelReadError('You can\'t read model data files without it\'s metadata')
            else:
                res_row = read_str(logger, row, row_map, delim, file_path)
                yield res_row   # возвращаем полученный набор
    raise StopIteration         # Файл закончился

    
def remap_str(str_, attr_list, file_map, defaults):     # Приводим строку данных к формату файла,
    res_str = list(defaults)
    for num in range(len(attr_list)):
        each = attr_list[num]
        res_str[file_map[each] - 1] = str_[num]
    return res_str


def remap_list(list_str, attr_list, file_map, defaults):    # Приводим данные к формату файла
    for num in range(len(list_str)):
        list_str[num] = remap_str(list_str[num], attr_list, file_map, defaults)
    

def str_list_refactor(row_map, str_, attr_list, file_map, defaults, no_remap=False):           # перекодировка строки через row_map
    if not no_remap: # only for check
        str_ = remap_str(str_, attr_list, file_map, defaults)
    for num in range(len(str_)):
        if str_[num] is None:                 # вместо None ставим пустую строку
            str_[num] = ''
        elif row_map[num] == DATE_VALUE:        # даты перекодируем через функцию
            str_[num] = quoting(dt.date_to_str(str_[num]))
        elif row_map[num] == DATETIME_VALUE:    # дату-время также прогоняем через отдельную функцию
            str_[num] = quoting(dt.datetime_to_str(str_[num]))
        else:
            str_[num] = quoting(str(str_[num])) # все остальное перекодируем через конструктор строки
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
    def __init__(self, data_path, get_logger, model_meta=None):
        if model_meta is None:
            self.model_meta = dict()    # создаем с пустым словарем
        else:
            self.model_meta = model_meta
        self.model_meta[DATA_PATH] = data_path
        self.logger = mu.Logger('ModelFileWorker', get_logger)

    log_func = mu.Decor._logger

    @log_func(default_debug=True)
    def _write_header(self, name):
        if name not in self.model_meta:
            self.logger.error('_write_header', 'Model {0} not found in dictionary'.format(name), er.ModelWriteError)
            raise er.ModelWriteError('Model {0} not found in dictionary'.format(name))
        model_dict = self.model_meta[name]
        path = self.model_meta[DATA_PATH] + name + HEADER_EXTENSION
        with open(path, 'w') as f:
            js.dump(model_dict, f)

    @log_func(default_debug=True)
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

    @log_func(default_debug=True)
    def _change_header(self, name, header):         # подменяем файл заголовка - потенциально опасно, ломает данные
        if name not in self.model_meta:             # если его не существовало - создаем
            self.model_meta[name] = dict()
        self.model_meta[name]= header
        self._write_header(name)                    # и пишем в файл

    @log_func(default_debug=True)
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
                part_name.append(dt.date_to_str(str_[num - 1], fmt))       # с форматом только даты
            else:
                part_name.append(str(str_[num - 1]))
        return delim.join(part_name)                                    # склеиваем разделителем

    @log_func(default_debug=True)
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

    @log_func(default_debug=True)
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

    @log_func()
    def _write_model_partition(self, model_name, partition_name, list_str, row_map, delim, mode, file_map, defaults, no_remap):
        """Write data to current partition of model data file"""
        self._validate_partition(model_name, partition_name, delim)
        with open(self.model_meta[DATA_PATH] + self.model_meta[model_name][PARTITION_FILES_KEY][partition_name], mode) as f:
            for str_ in list_str:
                write_str_to_model_data(f, row_map, str_, delim, list_str, file_map, defaults, no_remap)

    @log_func(default_debug=True)
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

    @log_func(default_debug=True)
    def _get_first_n_attrs(self, attr_dict, n=1):
        return list(attr_dict[each + 1][ATTRIBUTE_NAME_KEY] for each in range(n))

    @log_func()
    def _check_attr_list(self, model_name, list_str, attr_list, row_map, attr_dict, file_map):
        sample_str = list_str[0]
        self.logger.debug('_check_attr_list', model_name=model_name, sample_str=sample_str, attr_list=attr_list,
                          row_map=row_map, attr_dict=attr_dict, file_map=file_map)
        if attr_list is None:
            if len(sample_str) == len(row_map):
                return True
            else:
                return False
        if len(attr_list) != len(sample_str):
            self.logger.error('_check_attr_list', 'desync metadata: expected {0} attributes, but {1} attributes found'.format(
                len(attr_list), len(sample_str)
            ), er.ModelWriteError)
            # raise er.ModelWriteError('Error writing data: desync metadata: expected {0} attributes, but {1} attributes found'.format(
            #     len(attr_list), len(sample_str)
            # ))
        for each in attr_list:
            if each not in file_map:
                self.logger.error('_check_attr_list', 'attribute \'{0}\' not found in model \'{1}\''.format(
                    each, model_name
                ), er.ModelWriteError)
                # raise er.ModelWriteError('Error writing data: attribute \'{0}\' not found in model \'{1}\''.format(
                #     each, model_name
                # ))
        for num in range(len(attr_dict)):
            if num >= len(attr_list) or attr_dict[num + 1][ATTRIBUTE_NAME_KEY] != attr_list[num]:
                return False
        return True

    @log_func(default_debug=True)
    def _get_default_values(self, model_name):
        attr_dict = self.model_meta[model_name][ATTRIBUTE_KEY]
        res_list = list(range(len(attr_dict)))
        for each in range(len(attr_dict)):
            def_ = attr_dict[each + 1][OPTION_DEFAULT_KEY]
            typ_ = attr_dict[each + 1][ATTRIBYTE_TYPE_KEY]
            if typ_ not in (DATETIME_VALUE, DATE_VALUE) \
                or def_ in (dt.ACTUALITY_DTTM_VALUE, dt.ACTUALITY_DATE_VALUE, None):
                res_list[each] = def_
            elif typ_ == DATE_VALUE:
                res_list[each] = dt.str_to_date(def_)
            else:
                res_list[each] = dt.str_to_datetime(def_)
        return res_list

    @log_func()
    def write_model_data(self, name: str, list_str: list, attr_list=None, brutal=False):
        """Procedure writes model to data files (and do nothing with it's header)"""
        self.logger.debug('write_model_data', _name=name, attr_list=attr_list, brutal=brutal)
        if len(list_str) == 0:
            self.logger.error('write_model_data', 'there are no data to write (blank input)',er.ModelWriteError)
            # raise er.ModelWriteError('Error writing data: there are no data to write')
        if name not in self.model_meta:             # если к модели еще не обращались - пытаемся прочесть заголовок из файла
            try:
                self._read_header(name)
            except Exception:
                self.logger.error('write_model_data', 'Can\'t write data without it\'s header', er.ModelWriteError)
                # raise er.ModelWriteError('Can\'t write data without it\'s header')
        row_map = self._get_row_map(name)           # получаем карту строки
        delim = self.model_meta[name][FILE_DELIMITER_KEY]
        attr_dict = self.model_meta[name][ATTRIBUTE_KEY]
        defaults = self._get_default_values(name)
        file_map = self.get_file_map(name, header_validation=False)
        no_remap = self._check_attr_list(name, list_str, attr_list, row_map, attr_dict, file_map)
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

    @log_func(default_debug=True)
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
                    self.logger.note('del_model_files', 'File {} does not exist'.format(file))
                    pass                                                                # несуществующие файлы игнорируем
            try:
                os.rmdir(self.model_meta[DATA_PATH] + name)
            except FileNotFoundError:
                self.logger.note('del_model_files', 'Model data directory {} does not exist'.format(self.model_meta[DATA_PATH] + name))
                pass
            del self.model_meta[name]                                                   # удаляем модель из метаданных
            return True
        except Exception:
            return False

    @log_func()
    def replace_model_files(self, name: str, list_str: list, header=None):
        """Replace model files using data in memory"""
        if header is None:
            header = self.model_meta[name]                  # сохраняем актуальный заголовок в памяти

        try:
            self._read_header(name)                         # читаем старый заголовок
        except FileNotFoundError:
            self.logger.note('replace_model_files', 'Elder header does not exist; Exception ignored')
            pass                                            # если заголовка не было - просто пишем новый
        else:
            self.del_model_files(name)                      # удаляем всю модель
            os.mkdir(self.model_meta[DATA_PATH]+ name)      # создаем директорию для данных
            self._change_header(name, header)               # подменяем заголовок
        if len(list_str) > 0:
            self.write_model_data(name, list_str, brutal=True)  # пишем данные с перезаписью на всякий случай

    @log_func(default_debug=True)
    def _read_partition(self, model_name, part_name=DEFAULT_SINGLE_PARTITION_VAL, sel_attrs=None, file_map=None,
                        filter_=None):
        """read all strings in partition
            filtering structure: modelUtility.Filter"""
        file_path = self.model_meta[DATA_PATH] + self.model_meta[model_name][PARTITION_FILES_KEY][part_name]
        delimiter = self.model_meta[model_name][FILE_DELIMITER_KEY]
        row_map = self._get_row_map(model_name)
        res_list = list()
        if file_map is None and sel_attrs is not None:
            file_map = self.get_file_map(model_name, no_read_header=True)
        for each in read_model_data(self.logger, file_path, row_map, delimiter):
            if filter_ is not None:
                if filter_.resolve(each):
                    res_list.append(self._get_sel_attrs(each, file_map, sel_attrs))   #здесь еще надо бы фильтровать данные
            else:
                res_list.append(self._get_sel_attrs(each, file_map, sel_attrs))
        return res_list

    @log_func(default_debug=True)
    def read_model_data(self, name, partitions_=None, read_header=True, ignor_err_partitions=False, filter_=None,
                        selected=None):
        """Read full model or some partition list
            filtering not available yet"""
        if read_header:
            self._read_header(name)
        if name not in self.model_meta:
            self.logger.error('read_model_data', 'Can\'t read model data without it\'s header!', er.ModelReadError)
            # raise er.ModelReadError('Can\'t read model data without it\'s header!')
        part_list = list()
        if partitions_ is None:         # по умолчанию просто лезем во все партиции модели
            for each in self.model_meta[name][PARTITION_FILES_KEY]:
                part_list.append(each)
        elif type(partitions_) in (list, tuple):    # если передали список или кортеж, пробегаемся по нему
            for each in partitions_:
                if each in self.model_meta[name][PARTITION_FILES_KEY]:
                    part_list.append(each)
                elif not ignor_err_partitions:      # если не выставлен флаг игнорирования кривых партиций и такой партиции нет - падаем
                    self.logger.error('read_model_data', 'Wrong Partition name \'{0}\' for model \'{1}\''.format(each, name), er.ModelReadError)
                    # raise er.ModelReadError('Wrong Partition name \'{0}\' for model \'{1}\''.format(each, name))
        elif type(partitions_) == str:              # если передали строку - считаем что это имя партиции
            if partitions_ in self.model_meta[name][PARTITION_FILES_KEY]:
                part_list.append(partitions_)
            elif not ignor_err_partitions:          # опять падаем если она кривая и нет флага
                self.logger.error('read_model_data', 'Wrong Partition name \'{0}\' for model \'{1}\''.format(partitions_, name), er.ModelReadError)
                # raise er.ModelReadError('Wrong Partition name \'{0}\' for model \'{1}\''.format(partitions_, name))
        else:
            self.logger.error('read_model_data', 'Unknown format for partitions_ parameter: only lists, tuples and strings supported', er.ModelReadError)
            # raise er.ModelReadError('Unknown format for partitions_ parameter: only lists, tuples and strings supported')
        result = list()
        file_map = self.get_file_map(name, no_read_header=True)
        if filter_ is not None:
            fltr = filter_.try_resolve()
            if fltr is True:
                filter_ = None
            elif fltr is False:
                return []
            else:
                filter_.set_row_head(list(file_map.keys()))
        for each in part_list:                      # читаем все найденные партиции, если их нет - вернем пустой список
            result += self._read_partition(name, each, filter_=filter_, file_map=file_map, sel_attrs=selected)
        return result   # если не прочли ни одной партиции - на выходе будет пустой список

    @log_func()
    def insert_simple_data(self, model, str_, attr_list=None):
        """Will append a single string to a model file"""
        list_str = list()
        list_str.append(str_)
        self.write_model_data(model, list_str, attr_list)

    @log_func(default_debug=True)
    def _validate_header(self, name, header=None, validation_mode=True, brutal_read=False, no_read=False):
        """Function return model header"""
        if header is None:  # если заголовок не передали - пробуем его прочесть из метаданных или файла
            if name not in self.model_meta or brutal_read:
                if not no_read:
                    try:
                        self._read_header(name)
                    except FileNotFoundError:   # если ни то ни другое не выходит - падаем
                        self.logger.error('_validate_header', 'Unknown model \'{}\''.format(name), er.DataValidationError)
                        # raise er.DataValidationError('Header validation: Unknown model \'{}\''.format(name))
                else:
                    self.logger.error('_validate_header', 'Unknown model \'{}\''.format(name), er.DataValidationError)
                    # raise er.DataValidationError('Header validation: Unknown model \'{}\''.format(name))
            header = self.model_meta[name]
        if validation_mode: # начинаем проверку
            if type(header) != dict:    # заголовок должен быть словарем
                self.logger.error('_validate_header', 'You\'re header is not a dictionary!', er.DataValidationError)
                # raise er.DataValidationError('Header validation: You\'re header is not a dictionary!')
            if (ATTRIBUTE_KEY not in header or PK_ATTRIBUTE_KEY not in header or OPTIONS_KEY not in header\
                    or PARTITION_FILES_KEY not in header or PARTITION_ATTRIBUTE_KEY not in header\
                    or FILE_DELIMITER_KEY not in header):   # проверяем присутствие основных ключей заголовка
                self.logger.error('_validate_header', 'One or more critical parameters not found in header', er.DataValidationError)
                # raise er.DataValidationError('Header validation: One or more critical parameters not found in header')
            if OPTION_LOAD_KEY not in header[OPTIONS_KEY] \
                or header[OPTIONS_KEY][OPTION_LOAD_KEY] not in (APPEND_MODE, REPLACE_MODE): # проверяем режим загрузки модели
                self.logger.error('_validate_header', 'Correct model loading type not set for the model', er.DataValidationError)
                # raise er.DataValidationError('Header validation: Correct model loading type not set for the model')
            if type(header[ATTRIBUTE_KEY]) != dict or type(header[PARTITION_FILES_KEY]) != dict\
                    or type(header[PARTITION_ATTRIBUTE_KEY]) != dict or type(header[PK_ATTRIBUTE_KEY]) != int\
                    or not isinstance(header[FILE_DELIMITER_KEY], str): # проверяем типы основных ключей заголовка
                self.logger.error('_validate_header', 'One or more critical parameter types are incorrect in header', er.DataValidationError)
                # raise er.DataValidationError('Header validation: One or more critical parameter types are incorrect in header')
            for each in header[ATTRIBUTE_KEY]:  # Проверяем словарь атрибутов
                if type(each) != int:           # ключ обязательно int
                    self.logger.error('_validate_header', 'One or more key in attributes dictionary has not supported type ({})'.format(type(each)), er.DataValidationError)
                    # raise TypeError('Header validation: One or more key in attributes dictionary has not supported type ({})'.format(type(each)))
                if type(header[ATTRIBUTE_KEY][each]) != dict:   # соблюдение иерархии
                    self.logger.error('_validate_header', 'One or more critical parameter types are incorect in attributes dictionary', er.DataValidationError)
                    # raise er.DataValidationError('Header validation: One or more critical parameter types are incorect in attributes dictionary')
                if ATTRIBUTE_NAME_KEY not in header[ATTRIBUTE_KEY][each] or OPTION_HIDE_KEY not in header[ATTRIBUTE_KEY][each]\
                        or OPTION_DEFAULT_KEY not in header[ATTRIBUTE_KEY][each]\
                        or ATTRIBYTE_TYPE_KEY not in header[ATTRIBUTE_KEY][each]:   # проверяем присутствие основных параметров атрибута
                    self.logger.error('_validate_header', 'One or more critical parameters not found in attributes dictionary', er.DataValidationError)
                    # raise er.DataValidationError('Header validation: One or more critical parameters not found in attributes dictionary')
                if header[ATTRIBUTE_KEY][each][ATTRIBYTE_TYPE_KEY] not in DATA_TYPES_LIST:  # проверяем типы атрибутов
                    self.logger.error('_validate_header', 'Attribute \'{0}\' has incorrect type \'{1}\''.format(
                        header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY], header[ATTRIBUTE_KEY][each][ATTRIBYTE_TYPE_KEY]
                    ), er.DataValidationError)
                    # raise er.DataValidationError('Header validation: Attribute \'{0}\' has incorrect type \'{1}\''.format(
                    #     header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY], header[ATTRIBUTE_KEY][each][ATTRIBYTE_TYPE_KEY]
                    # ))
            for each in header[PARTITION_ATTRIBUTE_KEY]:    # теперь словарь партиций
                if type(each) != int:           # ключ обязательно int
                    self.logger.error('_validate_header', 'One or more key in partition dictionary has not supported type ({})'.format(type(each)), er.DataValidationError)
                    # raise er.DataValidationError('Header validation: One or more key in partition dictionary has not supported type ({})'.format(type(each)))
                if type(header[PARTITION_ATTRIBUTE_KEY][each]) != dict: # тоже иерархическая структура
                    self.logger.error('_validate_header', 'One or more critical parameter types are incorect in partition dictionary', er.DataValidationError)
                    # raise er.DataValidationError('Header validation: One or more critical parameter types are incorect in partition dictionary')
                if PARTITION_FIELD_NUM not in header[PARTITION_ATTRIBUTE_KEY][each]\
                        or PARTITION_FIELD_FORMAT not in header[PARTITION_ATTRIBUTE_KEY][each]: # ключевые параметры
                    self.logger.error('_validate_header', 'One or more critical parameters not found in partition dictionary', er.DataValidationError)
                    # raise er.DataValidationError('Header validation: One or more critical parameters not found in partition dictionary')
            for each in header[PARTITION_FILES_KEY]:    # словарь файлов данных
                if type(each) != str or not isinstance(header[PARTITION_FILES_KEY][each], str): # все параметры обязательно строковые
                    self.logger.error('_validate_header', 'On or more parameters has incorrect data type in partition files dictionary', er.DataValidationError)
                    # raise er.DataValidationError('Header validation: On or more parameters has incorrect data type in partition files dictionary')
        return header   # возвращаем корректный заголовок

    @log_func(default_debug=True)
    def _get_atr_num(self, name, atr, header=None):
        """Return place of current attribute in file using it's name
            (you can use other data source - not worker metadata)"""
        header = self._validate_header(name, header, validation_mode=False)    # валидируем header
        for each in header[ATTRIBUTE_KEY]:
            if header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY] == atr:
                return each
        return -1   # возвращаем "-1" если такого атрибута нет

    @log_func(default_debug=True)
    def get_file_map(self, name, header=None, no_read_header=False, header_validation=True):
        header = self._validate_header(name, header, validation_mode=header_validation, no_read=no_read_header)
        result_map = dict()
        for each in header[ATTRIBUTE_KEY]:
            result_map[header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY]] = each
        return result_map

    @log_func(default_debug=True)
    def add_attribute(self, model_name, attribute_name, attribute_type, **kwargs):
        header = self._validate_header(model_name)
        if attribute_type not in DATA_TYPES_LIST:   # проверяем валидность типа
            self.logger.error('add_attribute', 'Unknown data type \'{0}\' for attribute {1}'.format(attribute_type, attribute_name), er.ModelModifyError)
            # raise er.ModelModifyError('Unknown data type \'{0}\' for attribute {1}'.format(attribute_type, attribute_name))
        for each in header[ATTRIBUTE_KEY]:          # проверяем модель на существование добавляемого атрибута
            if header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY] == attribute_name:
                self.logger.error('add_attribute', '{0} already exist in model {1}'.format(attribute_name, model_name), er.ModelModifyError)
                # raise er.ModelModifyError('{0} already exist in model {1}'.format(attribute_name, model_name))
        num = len(header[ATTRIBUTE_KEY]) + 1        # номер нового атрибута
        header[ATTRIBUTE_KEY][num] = dict()         # дописываем в заголовок новый атрибут
        header[ATTRIBUTE_KEY][num][ATTRIBUTE_NAME_KEY] = attribute_name
        header[ATTRIBUTE_KEY][num][ATTRIBYTE_TYPE_KEY] = attribute_type
        header[ATTRIBUTE_KEY][num][OPTION_DEFAULT_KEY] = None   # кастомные опции будут дописаны позже ставим умолчания
        header[ATTRIBUTE_KEY][num][OPTION_HIDE_KEY] = False
        for each in kwargs:                                     # проставляем custom опции атрибутов
            if each == OPTION_DEFAULT_KEY:
                if attribute_type in (DATE_VALUE, DATETIME_VALUE) and kwargs[each] not in (dt.ACTUALITY_DATE_VALUE, dt.ACTUALITY_DTTM_VALUE):
                    if attribute_type == DATE_VALUE:
                        header[ATTRIBUTE_KEY][num][each] = dt.date_to_str(kwargs[each])
                    if attribute_type == DATETIME_VALUE:
                        header[ATTRIBUTE_KEY][num][each] = dt.datetime_to_str(kwargs[each])
                else:
                    header[ATTRIBUTE_KEY][num][each] = kwargs[each]
            else:
                header[ATTRIBUTE_KEY][num][each] = kwargs[each]
        self._validate_header(model_name, header, no_read=True) # проверяем новый заголовок
        self._change_header(model_name, header)                 # и подменяем его

    @log_func(default_debug=True)
    def rename_attribute(self, model_name, old_name, new_name):     # переименовывает атрибут (переписывает заголовок)
        header = self._validate_header(model_name, validation_mode=False)
        num = self._get_atr_num(model_name, old_name, header)       # ищем старое имя атрибута
        num_new = self._get_atr_num(model_name, new_name, header)   # ищем новое имя
        if num == -1:                                               # если не нашли старое - падаем
            self.logger.error('rename_attribute', 'model {0} hasn\'t attribute {1}'.format(model_name, old_name), er.ModelModifyError)
            # raise er.ModelModifyError('Error renaming attributes: model {0} hasn\'t attribute {1}'.format(model_name, old_name))
        elif num_new != -1:                                         # если нашли новое - падаем
            self.logger.error('rename_attribute', 'model {0} already has attribute {1}'.format(model_name, new_name), er.ModelModifyError)
            # raise er.ModelModifyError('Error renaming attributes: model {0} already has attribute {1}'.format(model_name, new_name))
        header[ATTRIBUTE_KEY][num][ATTRIBUTE_NAME_KEY] = new_name   # меняем имя в заголовке
        self._validate_header(model_name, header, validation_mode=True, no_read=True) # проверяем заголовок
        self._change_header(model_name, header)                     # подменяем заголовок

    # @log_func(default_debug=True)
    def _get_sel_attrs(self, str_, file_map, new_map=None):         # функция для реализации выборки конкретных атрибутов из строки в нужном порядке
        if new_map is None:                                         # если не передали список с атрибутами - возвращаем строку
            return str_
        res_str = list()    
        for each in new_map:
            if each not in file_map:                                # если в списке атрибутов есть "лишний" - падаем
                self.logger.error('_get_sel_attrs', 'Error selecting: Unknown attribute {0}'.format(str(each)), er.ModelReadError)
                # raise er.ModelReadError('Error selecting: Unknown attribute {0}'.format(str(each)))
            res_str.append(str_[file_map[each] - 1])                # если все ок, добавляем индекс атрибута в результирующий список
        return res_str

    @log_func(default_debug=True)
    def delete_attribute(self, model_name, attr_name, new_key_attr=None):           # удаление атрибута модели
        header = self._validate_header(model_name, validation_mode=False)
        num = self._get_atr_num(model_name, attr_name, header)
        new_key = -1
        if new_key_attr is not None:                                                # обрабатываем возможное удаление ключа модели
            new_key = self._get_atr_num(model_name, new_key_attr, header)
        part_level = -1
        if num == -1:                                                               # падаем на удалении несуществующего
            self.logger.error('delete_attribute', 'model {0} hasn\'t attribute {1}'.format(model_name, attr_name), er.ModelModifyError)
            # raise er.ModelModifyError('Error deleting attributes: model {0} hasn\'t attribute {1}'.format(model_name, attr_name))
        for each in header[PARTITION_ATTRIBUTE_KEY]:                                # обрабатываем возможное вхождение в партиции
            if header[PARTITION_ATTRIBUTE_KEY][each][PARTITION_FIELD_NUM] == num:
                part_level = each
        if header[PK_ATTRIBUTE_KEY] == num:
            if new_key == -1:                                                       # если действительно удаляем ключ, а нового нет - падаем
                self.logger.error('delete_attribute', 'delete key attribute with no new key attribute selected', er.ModelModifyError)
                # raise er.ModelModifyError('Error deleting attributes: delete key attribute with no new key attribute selected')
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

    @log_func(default_debug=True)
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
            self.logger.error('create_model', 'Model called \'{0}\' already exist: {1}'.format(name, str(self.model_meta[name])), er.ModelFileException)
            # raise er.ModelFileException('Model called \'{0}\' already exist: {1}'.format(name, str(self.model_meta[name])))
        header = dict()
        header[ATTRIBUTE_KEY] = dict()
        header[PARTITION_FILES_KEY] = dict()
        iter = 1    # итератор ключей словаря атрибутов
        pk_idx = -1 # индекс ключевого атрибута
        for each in attrs:
            if attrs[each] is None:
                self.logger.error('create_model', 'Attribute name cannot be None!', er.ModelFileException)
                # raise er.ModelFileException('Error model creating', 'Attribute name cannot be None!')
            header[ATTRIBUTE_KEY][iter] = dict()
            header[ATTRIBUTE_KEY][iter][ATTRIBUTE_NAME_KEY] = each
            header[ATTRIBUTE_KEY][iter][ATTRIBYTE_TYPE_KEY] = attrs[each]
            if each == key:
                pk_idx = iter   # если находим ключ сохраняем его индекс
            iter += 1
        if pk_idx == -1:    # если не нашли - падаем
            self.logger.error('create_model', 'You Can\'t create model without key: there are no attribute '
                           'called \'{0}\' in {1}'.format(key, str(attrs)), er.ModelFileException)
            # raise er.ModelFileException('You Can\'t create model without key: there are no attribute '
            #                'called \'{0}\' in {1}'.format(key, str(attrs)))
        header[PK_ATTRIBUTE_KEY] = pk_idx
        parts = dict()  # словарь для данных о партицировании
        header[PARTITION_ATTRIBUTE_KEY] = parts
        if partition is not None:
            iter = 1    # вновь задаем итератор для создания уровней партицирования
            for each in partition:
                header[PARTITION_ATTRIBUTE_KEY][iter] = dict()
                num = self._get_atr_num(name, each, header)
                if num == -1:   # падаем если не нашли атрибута с переданным именем
                    self.logger.error('create_model', 'There are no {0} attribute, can\'t create partition'.format(each), er.ModelFileException)
                    # raise er.ModelFileException('Error model creating: There are no {0} attribute, can\'t create partition'.format(each))
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
                self.logger.error('create_model', 'Unknown type for \'hide\' parameter! Use list or string!', er.ModelFileException)
                # raise er.ModelFileException('Error model creation: Unknown type for \'hide\' parameter! Use list or string!')
            if defaults is None:                                                    # выставляем значение по-умолчанию
                defaults = dict()
            defaults[ACTUALITY_FIELD_NAME] = dt.ACTUALITY_DTTM_VALUE
        elif load_mode == REPLACE_MODE:                                             # метод полной перезаписи модели
            header[OPTIONS_KEY][OPTION_LOAD_KEY] = REPLACE_MODE
        else:                                                                       # других пока не предусмотрено
            self.logger.error('create_model', 'Loading mode could be only {0} or {1}'.format(APPEND_MODE, REPLACE_MODE), er.ModelFileException)
            # raise er.ModelFileException('Error model creation: Loading mode could be only {0} or {1}'.format(APPEND_MODE, REPLACE_MODE))
        if type(hide) not in (list, str, type(None)):
            self.logger.error('create_model', 'Unknown type for \'hide\' parameter! Use list or string!', er.ModelFileException)
            # raise er.ModelFileException('Error model creation: Unknown type for \'hide\' parameter! Use list or string!')
        if type(defaults) not in (dict, type(None)):
            self.logger.error('create_model', 'Unknown type for \'default\' parameter! Use dictionary!', er.ModelFileException)
            # raise er.ModelFileException('Error model creation: Unknown type for \'default\' parameter! Use dictionary!')
        for each in header[ATTRIBUTE_KEY]:                                          # проставим опции атрибутов для представлений
            attr_name = header[ATTRIBUTE_KEY][each][ATTRIBUTE_NAME_KEY]
            attr_type = header[ATTRIBUTE_KEY][each][ATTRIBYTE_TYPE_KEY]
            if (type(defaults) == dict and attr_name in defaults):                  # значения по умолчанию
                if attr_type == DATE_VALUE and defaults[attr_name] != dt.ACTUALITY_DATE_VALUE:
                    if type(defaults[attr_name]) == str:
                        dt.str_to_date(defaults[attr_name])
                        def_ = defaults[attr_name]
                    else:
                        def_ = dt.date_to_str(defaults[attr_name])
                elif attr_type == DATETIME_VALUE and defaults[attr_name] != dt.ACTUALITY_DTTM_VALUE:
                    if type(defaults[attr_name]) == str:
                        dt.str_to_datetime(defaults[attr_name])
                        def_ = defaults[attr_name]
                    else:
                        def_ = dt.datetime_to_str(defaults[attr_name])
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

    @log_func(default_debug=True)
    def get_model_header(self, model_name): # просто читаем и отдаем заголовок
        self._read_header(model_name)
        return self.model_meta[model_name]

    @log_func(default_debug=True)
    def modify_attribute(self, model_name, modif_type, attr_name, **kwargs):
        """Типы модификаци: add, remove, rename
        """
        if modif_type == 'add':
            if ATTRIBYTE_TYPE_KEY not in kwargs:
                self.logger.error('modify_attribute', 'required parameter {} not found'.format(ATTRIBYTE_TYPE_KEY), er.ModelModifyError)
                # raise er.ModelModifyError('Error modify attribute: required parameter {} not found'.format(ATTRIBYTE_TYPE_KEY))
            self.add_attribute(model_name, attr_name, attribute_type=kwargs[ATTRIBYTE_TYPE_KEY], **kwargs)
        elif modif_type == 'rename':
            if 'new_name' not in kwargs:
                self.logger.error('modify_attribute', 'required parameter {} not found'.format('new_name'), er.ModelModifyError)
                # raise er.ModelModifyError('Error modify attribute: required parameter {} not found'.format('new_name'))
            self.rename_attribute(model_name, attr_name, kwargs['new_name'])
        elif modif_type == 'remove':
            if 'new_key_attr' in kwargs:
                new_key = kwargs['new_key_attr']
            else:
                new_key = None
            self.delete_attribute(model_name, attr_name, new_key)
        else:
            self.logger.error('modify_attribute', 'Unknown modification type {}'.format(modif_type), er.ModelModifyError)
            # raise ValueError('Unknown modification type {}'.format(modif_type))

    @log_func(default_debug=True)
    def modify_partition(self, model_name, modif_type, attr_name, attr_fmt=None):   # модифицирует словарь партиций вынести эту функцию в fileworker'a в модель
        if modif_type not in ('add', 'remove', 'reformat'):                         # неизвестные типы модификаций
            self.logger.error('modify_partition', 'unknown modification type \'{}\''.format(modif_type), er.ModelModifyError)
            # raise er.ModelModifyError('Error modifying partitioning for {0}: unknown modification type \'{1}\''.format(
            #     model_name, modif_type
            # ))
        header = self._validate_header(model_name, validation_mode=False)           # читаем заголовок
        num = self._get_atr_num(model_name, attr_name, header)
        if num == -1:                                                               # атрибут отсутствует в модели
            self.logger.error('modify_partition', 'Unknown attribute \'{1}\'', er.ModelModifyError)
            # raise er.ModelModifyError('Error modifying partitioning for {0}: Unknown attribute \'{1}\''.format(
            #     model_name, attr_name
            # ))
        attr_type = header[ATTRIBUTE_KEY][num][ATTRIBYTE_TYPE_KEY]                  # сохраняем тип атрибута
        if attr_type in (DATE_VALUE, DATETIME_VALUE) and modif_type in ('add', 'reformat'): # проверяем форма для дат при смене формата/добавлении партиции
            try:
                dt.datetime_to_str(dt.datetime.now(), attr_fmt)
            except Exception:
                self.logger.error('modify_partition', 'Incorrect format {} for date or datetime'.format(attr_fmt), er.ModelModifyError)
                # raise er.ModelModifyError('Error modifying partitioning for {0}: Incorrect format {1} for date or datetime'.format(
                #     model_name, attr_fmt
                # ))
        if modif_type == 'add':                                                     # добавление
            for each in header[PARTITION_ATTRIBUTE_KEY]:
                if header[PARTITION_ATTRIBUTE_KEY][each][PARTITION_FIELD_NUM] == num:   # проверка на то что партицирование по этому атрибуту уже есть
                    self.logger.error('modiy_partition', 'model {0} already partitioned by {1}'.format(
                        model_name, attr_name
                    ), er.ModelModifyError)
                    # raise er.ModelModifyError('Error modifying partitioning for {0}: model already partitioned by {1}'.format(
                    #     model_name, attr_name
                    # ))
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
                self.logger.error('modify_partition', 'model {0} don\'t partitioned by {1}'.format(
                    model_name, attr_name
                ), er.ModelModifyError)
                # raise er.ModelModifyError('Error modifying partitioning for {0}: model don\'t partitioned by {1}'.format(
                #     model_name, attr_name
                # ))
            if modif_type == 'reformat':                                            # если цель - смена формата - меняем значение соотв. ключа в словаре
                header[PARTITION_ATTRIBUTE_KEY][mod_part][PARTITION_FIELD_FORMAT] = attr_fmt
                if attr_type not in (DATETIME_VALUE, DATE_VALUE):
                    return True     # Костыль. Если меняем формат для не даты - возвращаем True, дальше ничего делать не надо
            else:
                max_part = len(header[PARTITION_ATTRIBUTE_KEY])                     # при удалении - меняем удаляемый атрибут с последним и удаляем последний
                header[PARTITION_ATTRIBUTE_KEY][mod_part] = header[PARTITION_ATTRIBUTE_KEY][max_part]
                del header[PARTITION_ATTRIBUTE_KEY][max_part]
        header[PARTITION_FILES_KEY] = dict()                # сносим невалидный словарь файлов модели
        data = self.read_model_data(model_name)                                     # читаем файлы модели
        self.replace_model_files(model_name, data, header)                          # переписываем файлы используя прочтенные данные

    @log_func(default_debug=True)
    def drop_partition(self, model_name, part_list, ignore_part_err=True):
        if isinstance(part_list, str):
            part_list = [part_list]
        elif part_list is None:
            self.logger.error('drop_partition', 'Partition name can not be None!', er.ModelModifyError)
            # raise er.ModelModifyError('Drop partition', 'Partition name can not be None!')
        header = self.get_model_header(model_name)
        part_dict = header[PARTITION_FILES_KEY]
        for each in part_list:
            if each not in part_dict:
                if not ignore_part_err:
                    self.logger.error('drop_partition', 'can\'t find \'{}\' partition'.format(each), er.ModelModifyError)
                    # raise er.ModelModifyError('Drop partition', 'can\'t find \'{}\' partition'.format(each))
            else:
                part_path = os.path.join(self.model_meta[DATA_PATH], part_dict[each])
                try:
                    os.remove(part_path)
                except IOError:
                    self.logger.error('drop_partition', 'error delete partition data file', er.ModelModifyError)
                    # raise er.ModelModifyError('Drop partition', 'error delete partition data file')
                del header[PARTITION_FILES_KEY][each]
        self._change_header(model_name, header)

    @log_func(default_debug=True)
    def copy_model(self, exist_model, new_model):
        header = self.get_model_header(exist_model)
        os.mkdir(self.model_meta[DATA_PATH] + new_model)
        self._change_header(new_model, header)

    @log_func(default_debug=True)
    def _get_partition_header(self, header):
        attrs_dict = header[ATTRIBUTE_KEY]
        parts = header[PARTITION_ATTRIBUTE_KEY]
        if len(parts) == 0:
            return None
        res = list()
        for num in range(len(parts)):
            res.append(attrs_dict[parts[num + 1][PARTITION_FIELD_NUM]][ATTRIBUTE_NAME_KEY])
        return res

    @log_func(default_debug=True)
    def get_parts_list(self, model_name, fltr : mu.Filter):
        header = self.get_model_header(model_name)
        tmp = list(header[PARTITION_FILES_KEY].keys())
        if fltr is None:
            return tmp
        lst = self._get_partition_header(header)
        fltr.set_row_head(lst)
        if lst is None:
            return [DEFAULT_SINGLE_PARTITION_VAL]
        if len(tmp) == 1:
            return tmp
        part_map = list()
        for num in range(len(header[ATTRIBUTE_KEY])):
            if header[ATTRIBUTE_KEY][num + 1][ATTRIBUTE_NAME_KEY] in lst:
                part_map.append(header[ATTRIBUTE_KEY][num + 1][ATTRIBYTE_TYPE_KEY])
        fmt = None
        for num in range(len(part_map)):
            each = part_map[num]
            if each in (DATE_VALUE, DATETIME_VALUE):
                fmt = header[PARTITION_ATTRIBUTE_KEY][num + 1][PARTITION_FIELD_FORMAT]
                break
        result = list()
        for each in tmp:
            temp_str = read_str(self.logger, each, part_map, header[FILE_DELIMITER_KEY], 'header', True, fmt)
            if fltr.resolve(temp_str):
                result.append(each)
        return result

    @log_func(default_debug=True)
    def get_model_key(self, model_name):
        if model_name not in self.model_meta:
            self._read_header(model_name)
        return self.model_meta[model_name][PK_ATTRIBUTE_KEY]

    @log_func(default_debug=True)
    def truncate_model_data(self, model_name):
        if model_name not in self.model_meta:
            self._read_header(model_name)
        header = self.model_meta[model_name]
        path = os.path.join(self.model_meta[DATA_PATH], model_name)
        oe.extended_remove(path, recursive=True)
        header[PARTITION_FILES_KEY] = dict()
        self._change_header(model_name, header)

    @log_func(default_debug=True)
    def get_row_map(self, model_name):
        if model_name not in self.model_meta:
            self._read_header(model_name)
        attr_dict = self.model_meta[model_name][ATTRIBUTE_KEY]
        res = list()
        for num in range(len(attr_dict)):
            res.append(attr_dict[num + 1][ATTRIBUTE_NAME_KEY])
        return res


if __name__ == '__main__' and DEBUG:
    a = ModelFileWorker(home)
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
    a.insert_simple_data('New_model', ['k5', 'i10', dt.datetime(2000,11,10,5,30), None, dt.ACTUALITY_DTTM_VALUE, 3.5])
    a.insert_simple_data('New_model', ['k5', 'i10', dt.datetime(2000, 11, 10, 5, 30), dt.date(2018, 4, 1), dt.ACTUALITY_DTTM_VALUE, 321365654438433452456475864674.5123456789])
    a.insert_simple_data('New_model', ['k6', dt.date(2017,5,14)], ['key_field', 'date_field'])
    a.modify_partition('New_model', 'remove', 'date_field')
    a.modify_partition('New_model', 'add', 'date_field', 'YYYYMMDD')
    a.modify_partition('New_model', 'reformat', 'date_field','YYYYMM')
    sel = ['date_field', 'floating_data', 'key_field']
    fltr = mu.Filter()
    fltr.set_clause("key_field not in ('k1', 'k2')")
    print(a.read_model_data('New_model', selected=sel, filter_=fltr))
    fltr.set_clause('date_field is not None')
    print(a.model_meta['New_model'][PARTITION_FILES_KEY])
    print(a.get_parts_list('New_model', fltr))
    print(a.read_model_data('New_model'))
    print(a.get_file_map('New_model'))
    print(a._get_row_map('New_model'))