import modelFile as mf
import os
import dates as dt
import modelUtility as mu


WORKERS_MODEL_NAME = 'Workers'
MODELS_MODEL_NAME = 'Models'
IDS_MODEL_NAME = 'Meta_id_sequence'
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
MAIN_BASE_NAME = 'Main'


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
    'load_mode': mf.APPEND_MODE
}


def get_self_dir():
    return os.path.curdir


def revalidate_path(path, recursive=False):
    if not recursive:
        if not os.path.exists(path):
            os.mkdir(path)
            return False
        return True
    else:
        path = path.strip(os.path.sep)
        tmp_path = path.split(os.path.sep)
        pth = tmp_path[0] + os.path.sep
        res = True
        for each in tmp_path[1 :]:
            pth = os.path.join(pth, each)
            if not os.path.exists(pth):
                os.mkdir(pth)
                res = False
        return res


def chek_file(path):
    return os.path.exists(path)


def get_meta_path(home_dir):
    return home_dir + 'Metadata\\'


def get_data_path(home_dir):
    return home_dir + 'Data\\'

def get_worker_path(home_dir, worker_name):
    data_path = get_data_path(home_dir)
    return data_path + worker_name + '\\'


def create_meta(home_dir=None):
    home_dir = home_dir or get_self_dir()
    meta_dir = get_meta_path(home_dir)
    data_dir = get_data_path(home_dir)
    main_base_dir = data_dir + MAIN_BASE_NAME + '\\'
    revalidate_path(home_dir, True)
    revalidate_path(meta_dir)
    revalidate_path(data_dir)
    revalidate_path(main_base_dir)
    worker = mf.ModelFileWorker(meta_dir)
    worker.create_model(**MODEL_WORKERS_DICT)
    worker.insert_simple_data(WORKERS_MODEL_NAME, [MAIN_BASE_NAME, main_base_dir],
                              [ATTR_WORKER_NAME, ATTR_WORKER_DIR])
    worker.create_model(**MODEL_ID_GEN_DICT)
    worker.create_model(**MODEL_MODELS_DICT)
    return worker


def add_worker(meta_worker : mf.ModelFileWorker, home_dir, worker_name):
    path = get_worker_path(home_dir, worker_name)
    meta_worker.insert_simple_data(WORKERS_MODEL_NAME, [worker_name, path],
                                   [ATTR_WORKER_NAME, ATTR_WORKER_DIR])
    return mf.ModelFileWorker(path)


def add_model(meta_worker : mf.ModelFileWorker, worker_name, model_name, model_header):
    lst_ = list()
    parts = list()
    condition = ATTR_MODEL_WORKER + ' = \'' + worker_name + '\' and ' + ATTR_MODEL_MODEL + ' = \'' + model_name + '\''
    fltr = mu.Filter()
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
        inn_lst += [attr[mf.OPTION_HIDE_KEY], attr[mf.OPTION_DEFAULT_KEY]]
        lst_.append(inn_lst)
    attr_list = [ATTR_ID, ATTR_MODEL_WORKER, ATTR_MODEL_MODEL, ATTR_MODEL_ATTR_NAME, ATTR_MODEL_ATTR_TYPE,
                 ATTR_MODEL_PARTITION, ATTR_MODEL_HIDE, ATTR_MODEL_DEFAULT]
    meta_worker.write_model_data(MODELS_MODEL_NAME, lst_, attr_list, brutal=False)
    attr_list = [ATTR_MODEL_WORKER, ATTR_MODEL_MODEL, ATTR_ID_GEN_MAX]
    fltr.set_clause('not (' + condition + ')')
    id_list = meta_worker.read_model_data(IDS_MODEL_NAME, filter_=fltr, selected=attr_list)
    id_list.append([worker_name, model_name, id])
    meta_worker.write_model_data(IDS_MODEL_NAME, id_list, attr_list, brutal=True)


if __name__ == '__main__':
    pass
