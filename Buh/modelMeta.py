import modelFile as mf
import os
import dates as dt
import modelUtility as mu
import osExtension as oe
import modelExceptions as me
import config
from modelUtility import (get_log_path, get_log_dir, get_worker_path, get_meta_path, get_data_path)
import time as tm


# Все модели создаем в режиме REPLACE, чтобы не добавлять лишних атрибутов


WORKERS_MODEL_NAME = 'Workers'
MODELS_MODEL_NAME = 'Models'
CONFIG_MODEL_NAME = 'Config'
IDS_MODEL_NAME = 'Meta_id_sequence'
ATTR_CONFIG_NAME = 'name'
ATTR_CONFIG_VALUE = 'value'
ATTR_ID_GEN_MAX = 'current_max'
ATTR_MODEL_WORKER = 'worker_name'
ATTR_MODEL_MODEL = 'model_name'
ATTR_MODEL_ATTR_NAME = 'attribute_name'
ATTR_MODEL_ATTR_TYPE = 'attribute_type'
ATTR_MODEL_PARTITION = 'partition_flag'
ATTR_MODEL_HIDE = 'hide_flg'
ATTR_MODEL_CREATED = 'create_timestamp'
ATTR_MODEL_DEFAULT = 'default_value'
ATTR_ID = 'row_id'
ATTR_WORKER_NAME = 'worker_name'
ATTR_WORKER_DIR = 'data_directory'
META_DEFAULT_DELIMITER = '|^|'
CONFIG_DELIMITER = '|^^|'
MAIN_BASE_NAME = 'Main'
DEFAULT_WORKER_NAME = 'default_worker'
DEFAULT_DELIMITER_NAME = 'default_delimiter'
DEFAULT_VIEW_TYPE_NAME = 'default_view_type'
VIEW_DATA = 'dictionary'
SIMPLE_DATA = 'simple'
ZIP_DATA_NAME = 'zip_data'                      #пока не планируется реализовывать
NOT_ZIP_DATA = 'no'
ZIP_DATA = 'yes'
DEFAULT_MODEL_LOAD_MODE = 'default_load_mode'
CONFIG_FILE_NAME = 'modelmeta.cfg'



MODEL_WORKERS_DICT = {
    'name': WORKERS_MODEL_NAME,
    'attrs': {ATTR_WORKER_NAME: 'str', ATTR_WORKER_DIR: 'str'},
    'key': ATTR_WORKER_NAME,
    'partition': None,
    'delim': META_DEFAULT_DELIMITER,
    'defaults': None,
    'hide': None,
    'load_mode': mf.REPLACE_MODE
}


MODEL_ID_GEN_DICT = {
    'name': IDS_MODEL_NAME,
    'attrs': {ATTR_MODEL_WORKER: 'str', ATTR_MODEL_MODEL: 'str', ATTR_ID_GEN_MAX: 'int'},
    'key': ATTR_MODEL_MODEL,
    'partition': None,
    'delim': META_DEFAULT_DELIMITER,
    'defaults': None,
    'hide': None,
    'load_mode': mf.REPLACE_MODE
}


MODEL_MODELS_DICT = {
    'name': MODELS_MODEL_NAME,
    'attrs': {
        ATTR_ID: 'int',
        ATTR_MODEL_WORKER: 'str',
        ATTR_MODEL_MODEL: 'str',
        ATTR_MODEL_ATTR_NAME: 'str',
        ATTR_MODEL_ATTR_TYPE: 'str',
        ATTR_MODEL_PARTITION: 'int',
        ATTR_MODEL_HIDE: 'int',
        ATTR_MODEL_DEFAULT: 'str',
        ATTR_MODEL_CREATED: 'dttm'
    },
    'key': ATTR_ID,
    'partition': {ATTR_MODEL_WORKER: None, ATTR_MODEL_MODEL: None},
    'delim': META_DEFAULT_DELIMITER,
    'defaults': {ATTR_MODEL_CREATED: dt.ACTUALITY_DTTM_VALUE},
    'hide': ATTR_ID,
    'load_mode': mf.REPLACE_MODE
}


MODEL_CONFIG_DICT = {
    'name': CONFIG_MODEL_NAME,
    'attrs': {
        ATTR_CONFIG_NAME: 'str',
        ATTR_CONFIG_VALUE: 'str'
    },
    'key': ATTR_CONFIG_NAME,
    'partition': None,
    'delim': CONFIG_DELIMITER,
    'defaults': None,
    'hide': None,
    'load_mode': mf.REPLACE_MODE
}


DEFAULT_CONFIG_DICT = {
    DEFAULT_WORKER_NAME: MAIN_BASE_NAME,
    DEFAULT_DELIMITER_NAME: META_DEFAULT_DELIMITER,
    ZIP_DATA_NAME: NOT_ZIP_DATA,
    DEFAULT_VIEW_TYPE_NAME: VIEW_DATA,
    DEFAULT_MODEL_LOAD_MODE: mf.REPLACE_MODE
}


# def get_self_dir():
#     return os.path.curdir


# def revalidate_path(path, recursive=False):
#     if not recursive:
#         if not os.path.exists(path):
#             os.mkdir(path)
#             return False
#         return True
#     else:
#         path = path.strip(os.path.sep)
#         tmp_path = path.split(os.path.sep)
#         pth = tmp_path[0] + os.path.sep
#         res = True
#         for each in tmp_path[1 :]:
#             pth = os.path.join(pth, each)
#             if not os.path.exists(pth):
#                 os.mkdir(pth)
#                 res = False
#         return res


# def chek_file(path):
#     return os.path.exists(path)


# def get_meta_path(home_dir):
#     return os.path.join(home_dir, 'Metadata') + os.path.sep


# def get_data_path(home_dir):
#     return os.path.join(home_dir, 'Data') + os.path.sep


# def get_worker_path(home_dir, worker_name):
#     data_path = get_data_path(home_dir)
#     return os.path.join(data_path, worker_name) + os.path.sep


# def get_log_dir(home_dir):
#     return os.path.join(home_dir, 'Log')


# def get_log_path(home_dir):
#     log_path = get_log_dir(home_dir)
#     return os.path.join(log_path, 'main_log.log')

def set_default_config(config : config.Config):
    config.auto_save = False
    for each in DEFAULT_CONFIG_DICT:
        config[each] = DEFAULT_CONFIG_DICT[each]
    config.save()
    config.auto_save = True
    # res = list()
    # for each in DEFAULT_CONFIG_DICT:
    #     res.append([each, DEFAULT_CONFIG_DICT[each]])
    # worker.write_model_data(CONFIG_MODEL_NAME, res, [ATTR_CONFIG_NAME, ATTR_CONFIG_VALUE], brutal=True)


# def get_config(worker : mf.ModelFileWorker):
#     try:
#         data = worker.read_model_data(CONFIG_MODEL_NAME, selected=[ATTR_CONFIG_NAME, ATTR_CONFIG_VALUE])
#     except IOError:
#         set_default_config(worker)
#         data = DEFAULT_CONFIG_DICT
#     res_dict = dict()
#     for each in data:
#         res_dict[each[0]] = each[1]
#     return res_dict

def drop_all(home_dir, save_income_path=False):
    oe.extended_remove(home_dir, recursive=True, ignore_errors=True, save_income_path=save_income_path)


def create_meta(home_dir=None):
    home_dir = home_dir or oe.get_self_dir()
    meta_dir = get_meta_path(home_dir)
    data_dir = get_data_path(home_dir)
    log_dir = get_log_dir(home_dir)
    main_base_dir = data_dir + MAIN_BASE_NAME + '\\'
    oe.revalidate_path(home_dir, True)
    oe.revalidate_path(log_dir)
    oe.revalidate_path(meta_dir)
    oe.revalidate_path(data_dir)
    oe.revalidate_path(main_base_dir)
    inner_logger = mu.Logger('MetaDataCreator', get_log_path(home_dir))
    inner_logger.log('create metadata', 'start')
    worker = mf.ModelFileWorker(meta_dir)
    worker.create_model(**MODEL_WORKERS_DICT)
    worker.insert_simple_data(WORKERS_MODEL_NAME, [MAIN_BASE_NAME, main_base_dir],
                              [ATTR_WORKER_NAME, ATTR_WORKER_DIR])
    worker.create_model(**MODEL_ID_GEN_DICT)
    worker.create_model(**MODEL_MODELS_DICT)
    worker.create_model(**MODEL_CONFIG_DICT)
    inner_logger.log('create metadata', 'ended successfully')
    # set_default_config(worker)
    return worker


def add_worker(meta_worker : mf.ModelFileWorker, home_dir, worker_name):
    path = get_worker_path(home_dir, worker_name)
    meta_worker.insert_simple_data(WORKERS_MODEL_NAME, [worker_name, path],
                                   [ATTR_WORKER_NAME, ATTR_WORKER_DIR])
    return mf.ModelFileWorker(path)


def drop_worker(meta_worker : mf.ModelFileWorker, worker_name, worker_path, filter):
    in_clause = ATTR_MODEL_WORKER + ' = \'' + worker_name + '\''
    out_clause = ATTR_MODEL_WORKER + ' <> \'' + worker_name + '\''
    filter.set_clause(in_clause)
    parts = meta_worker.get_parts_list(MODELS_MODEL_NAME, filter)
    meta_worker.drop_partition(MODELS_MODEL_NAME, parts)
    filter.set_clause(out_clause)
    data = meta_worker.read_model_data(IDS_MODEL_NAME, filter_=filter)
    if len(data) > 0:
        meta_worker.write_model_data(IDS_MODEL_NAME, data, brutal=True)
    else:
        meta_worker.truncate_model_data(IDS_MODEL_NAME)
    data = meta_worker.read_model_data(WORKERS_MODEL_NAME, filter_=filter)
    if len(data) > 0:
        meta_worker.write_model_data(WORKERS_MODEL_NAME, data, brutal=True)
    else:
        meta_worker.truncate_model_data(WORKERS_MODEL_NAME)
    del data
    oe.extended_remove(worker_path, recursive=True, save_income_path=False)


def add_model(meta_worker : mf.ModelFileWorker, worker_name, model_name, model_header, fltr : mu.Filter):
    lst_ = list()
    parts = list()
    condition = ATTR_MODEL_WORKER + ' = \'' + worker_name + '\' and ' + ATTR_MODEL_MODEL + ' = \'' + model_name + '\''
    fltr.set_clause(condition)
    id = meta_worker.read_model_data(IDS_MODEL_NAME, filter_=fltr, selected=ATTR_ID_GEN_MAX)
    if len(id) == 0:
        id = 0
    else:
        id = id[0][0]
    for each in model_header[mf.PARTITION_ATTRIBUTE_KEY]:
        parts.append(model_header[mf.PARTITION_ATTRIBUTE_KEY][each][mf.PARTITION_FIELD_NUM])
    for each in model_header[mf.ATTRIBUTE_KEY]:
        id += 1
        attr = model_header[mf.ATTRIBUTE_KEY][each]
        inn_lst = list()
        inn_lst.append(id)
        inn_lst += [worker_name, model_name, attr[mf.ATTRIBUTE_NAME_KEY], attr[mf.ATTRIBYTE_TYPE_KEY]]
        if each in parts:
            inn_lst.append(1)
        else:
            inn_lst.append(0)
        if attr[mf.OPTION_HIDE_KEY]:
            inn_lst.append(1)
        else:
            inn_lst.append(0)
        inn_lst.append(str(attr[mf.OPTION_DEFAULT_KEY]))
        lst_.append(inn_lst)
    attr_list = [ATTR_ID, ATTR_MODEL_WORKER, ATTR_MODEL_MODEL, ATTR_MODEL_ATTR_NAME, ATTR_MODEL_ATTR_TYPE,
                 ATTR_MODEL_PARTITION, ATTR_MODEL_HIDE, ATTR_MODEL_DEFAULT]
    meta_worker.write_model_data(MODELS_MODEL_NAME, lst_, attr_list, brutal=False)
    attr_list = [ATTR_MODEL_WORKER, ATTR_MODEL_MODEL, ATTR_ID_GEN_MAX]
    fltr.set_clause('not (' + condition + ')')
    id_list = meta_worker.read_model_data(IDS_MODEL_NAME, filter_=fltr, selected=attr_list)
    id_list.append([worker_name, model_name, id])
    meta_worker.write_model_data(IDS_MODEL_NAME, id_list, attr_list, brutal=True)


def start_meta(home_dir, brutal):
    meta_path = get_meta_path(home_dir)
    if not os.path.exists(meta_path) or brutal:
        return create_meta(home_dir)
    else:
        return mf.ModelFileWorker(meta_path)


class ModelMeta:
    def __init__(self, home_dir, brutal=False):
        self.model_path = home_dir
        self.filter = mu.Filter()
        self.worker = start_meta(home_dir, brutal)
        self.logger = mu.Logger('ModelMeta', get_log_path(home_dir))
        try:
            data_workers = self.worker.read_model_data(WORKERS_MODEL_NAME)
            for each in data_workers:
                each[1] = mf.ModelFileWorker(each[1])
            self.data_workers = mu.build_simple_view(data_workers, self.worker.get_model_key(WORKERS_MODEL_NAME))
            conf_file = os.path.join(get_meta_path(home_dir), CONFIG_FILE_NAME)
            self.config = config.Config(conf_file)
            if len(self.config) == 0:
                set_default_config(self.config)
        except:
            self.logger.log('metadata initialization', 'Error', 'can\'t read model metadata')
            raise me.ModelMetaException('Error metadata initializing', 'Can\'t read model metadata, it\'s broken!')

    log_func = mu.Decor._logger

    @log_func('add data worker')
    def add_data_worker(self, worker_name):
        self.logger.log('DEBUG', 'worker name: {}'.format(worker_name))
        path = get_worker_path(self.model_path, worker_name)
        if os.path.exists(path):
            self.logger.log('add data worker', 'Error', 'worker already exist')
            raise me.ModelMetaException('Add data worker Error', 'Worker called {} already exist!'.format(worker_name))
        oe.revalidate_path(path)
        self.data_workers[worker_name] = add_worker(self.worker, self.model_path, worker_name)
        return self.data_workers[worker_name]

    @log_func('drop worker from metadata')
    def drop_data_worker(self, worker_name):
        self.logger.log('DEBUG', 'worker name: {}'.format(worker_name))
        path = get_worker_path(self.model_path, worker_name)
        if not (os.path.exists(path)):
            raise me.ModelMetaException('Drop data worker Error', 'Worker called {} does not exist!'.format(worker_name))
        if worker_name not in self.data_workers:
            raise me.ModelMetaException('Drop data worker Error', 'Worker called {} not found in model metadata!'.format(worker_name))
        drop_worker(self.worker, worker_name, path, self.filter)
        del self.data_workers[worker_name]

    @log_func('add model to metadata')
    def add_data_model(self, worker_name, model_name, model_header):
        self.logger.log('DEBUG', 'worker name: {0}; model name: {1}'.format(worker_name, model_name))
        add_model(self.worker, worker_name, model_name, model_header, self.filter)

    @log_func('reset model config to default')
    def reset_config_to_default(self):
        set_default_config(self.config)

    @log_func('drop model from metadata')
    def drop_data_model(self, worker_name, model_name):
        clause = ATTR_MODEL_WORKER + ' = \'' + worker_name + '\' and ' + ATTR_MODEL_MODEL + ' = \'' + model_name + '\''
        part_list = self.worker.get_parts_list(MODELS_MODEL_NAME, self.filter.set_clause(clause))
        self.worker.drop_partition(MODELS_MODEL_NAME, part_list)

    @log_func('modify model')
    def modify_data_model(self, worker_name, model_name, model_header):
        self.logger.log('DEBUG', 'worker name: {0}; model name: {1}'.format(worker_name, model_name))
        self.drop_data_model(worker_name, model_name)
        add_model(self.worker, worker_name, model_name, model_header, self.filter)

    @log_func('get hidden model attribute list')
    def get_model_hide_list(self, worker_name, model_name):
        self.logger.log('DEBUG', 'worker name: {0}; model name: {1}'.format(worker_name, model_name))
        clause = ATTR_MODEL_WORKER + ' = \'' + worker_name + '\' and ' + ATTR_MODEL_MODEL + ' = \'' + model_name + '\''
        self.filter.set_clause(clause)
        part_list = self.worker.get_parts_list(MODELS_MODEL_NAME, self.filter)
        clause = ATTR_MODEL_HIDE + ' = ' + str(1)
        self.filter.set_clause(clause)
        tmp_res = self.worker.read_model_data(MODELS_MODEL_NAME, part_list, filter_=self.filter,
                                              selected=[ATTR_MODEL_ATTR_NAME])
        res = list()
        for each in tmp_res:
            res.append(each[0])
        return res


    # def get_id

    # def set_id

if __name__ == '__main__':
    pass
