import modelFile as mf
import os
import dates as dt


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
        tmp_path = path.split('\\')
        pth = tmp_path[0] + '\\'
        res = True
        for each in tmp_path[1 :]:
            pth = pth + each + '\\'
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


def add_model(model_header):
    pass


if __name__ == '__main__':
    pass
