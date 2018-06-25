import modelExceptions as me
import modelUtility as mu
import osExtension as oe
import modelMeta as mm
import modelFile as mf
import ModelTemplate as mt
import ModelView as mv
import logFile as lf
# from functools import wraps


class ModelManager:

    TNone = mt.ModelTemplate.TNone

    def __init__(self, model_directory, recreate_flg=False):
        self.model_directory = model_directory
        if recreate_flg:
            self._drop_all()
        oe.revalidate_path(model_directory, True)
        log_file_path = mu.get_log_path(model_directory)
        oe.revalidate_path(mu.get_log_dir(model_directory))
        self.log_generator = lf.get_log_file(mu.MainLog, log_file_path, reopen_if_closed=True)
        self.meta = mm.ModelMeta(model_directory, self.log_generator)
        self.logger = mu.Logger('ModelManager', self.log_generator)
        self.template = None
        self._closed = False

    log_func = mu.Decor._logger
    default_log = mu.Decor._logger(default_debug=True)
    check = mu.Decor._check_closed

    @property
    def closed(self):
        return self._closed

    @check
    def close_model(self):
        self.logger.note('close_model', 'model manager is closed now')
        self.logger.logger.close()
        self._closed = True

    def reopen_log(self):
        self.logger.logger.reopen()
        self.logger.note('reopen_log', 'log file has been reopened')

    @check
    @log_func()
    def add_worker(self, worker_name):
        self.logger.debug('add_worker', worker_name=worker_name)
        self.meta.add_data_worker(worker_name, self.log_generator)

    @check
    @log_func()
    def drop_worker(self, worker_name):
        self.logger.debug('drop_worker', worker_name=worker_name)
        if worker_name not in self.meta.data_workers:
            self.logger.error('drop worker', 'worker does not exist')
            raise me.ModelManagerException('Drop worker error', worker_name, 'worker does not exist!')
        path = mm.get_worker_path(self.model_directory, worker_name)
        oe.extended_remove(path, True)
        self.meta.drop_data_worker(worker_name)

    def _drop_all(self):
        oe.extended_remove(self.model_directory, True, save_extension='log')

    @check
    @log_func()
    def drop_all(self):
        self._drop_all()

    def _revalidate_worker(self, worker_name):
        if worker_name is None:
            self.logger.note('_revalidate_worker', 'worker not defined, default worker will be used')
            worker_name = self.meta.config[mm.DEFAULT_WORKER_NAME]
        return worker_name

    @check
    @log_func()
    def create_model(self, model_dictionary, model_worker=None):
        model_worker = self._revalidate_worker(model_worker)
        if 'delim' not in model_dictionary:
            self.logger.note('create_model', 'delimiter not defined, default delimiter will be used')
            model_dictionary['delim'] = self.meta.config[mm.DEFAULT_DELIMITER_NAME]
        if 'load_mode' not in model_dictionary:
            self.logger.note('create_model', 'loading mode not defined, default loading mode will be used')
            model_dictionary['load_mode'] = self.meta.config[mm.DEFAULT_MODEL_LOAD_MODE]
        name = model_dictionary['name']
        if model_worker not in self.meta.data_workers:
            self.logger.error('create_model', 'worker {} does not exist'.format(model_worker))
            raise me.ModelManagerException('create_model', name, 'worker \'{}\' does not exist'.format(model_worker))
        worker = self.meta.data_workers[model_worker]
        worker.create_model(**model_dictionary)
        self.meta.add_data_model(model_worker, name, worker.get_model_header(name))

    @check
    @log_func()
    def create_model_from_json(self, file_path):
        self.logger.debug('create_model_from_json', file_path=file_path)
        dic = mt.create_models_from_file(file_path, self.log_generator, self.logger, True)
        if 'worker' in dic:
            worker = dic['worker']
        else:
            worker = None
        del dic['worker']
        self.create_model(dic, worker)

    @check
    @log_func()
    def create_models_from_script(self, file_path):
        self.logger.debug('create_models_from_script', file_path=file_path)
        model_templates = mt.create_models_from_file(file_path, self.log_generator, self.logger)
        for each in model_templates:
            self.create_model(each.compile(), each.get_worker())

    @check
    @log_func()
    def create_new_template(self, model_name, model_attrs=None, model_partition=None, model_key=None, model_delimiter=None,
                         attr_defaults=None, model_worker=None, hide_attrs=None, load_mode=None):
        if self.template is not None:
            self.logger.error('create_new_template', 'current template doesn\'t empty', me.ModelManagerException)
            # raise me.ModelManagerException('Create new template', model_name, 'Template is not empty! ({})'.format(self.template))
        self.template = mt.ModelTemplate(model_name, self.log_generator, model_attrs, model_partition, model_key, model_delimiter,
                                         attr_defaults, model_worker, hide_attrs, load_mode)

    def _check_template_exist(self, err_msg):
        if self.template is None:
            self.logger.error('_check_template_exist', err_msg + ': current template is empty', me.ModelManagerException)
            # raise me.ModelManagerException(err_msg, 'there are no template to modify')

    @check
    @log_func()
    def template_add_attr(self, attr_name, attr_type, key=False, partition=TNone, default=TNone, hide=False):
        self._check_template_exist('template_add_attr')
        self.template.add_attr(attr_name, attr_type, key, partition, default, hide)

    @check
    @log_func()
    def template_add_partition(self, attr_name, attr_fmt):
        self._check_template_exist('template_add_partition')
        self.template.add_partition(attr_name, attr_fmt)

    @check
    @log_func()
    def template_set_key(self, key_attr):
        self._check_template_exist('template_set_key')
        self.template.set_key(key_attr)

    @check
    @log_func()
    def template_hide_attr(self, attr_name):
        self._check_template_exist('template_hide_attr')
        self.template.hide_attr(attr_name)

    @check
    @log_func()
    def template_add_default(self, attr_name, attr_value):
        self._check_template_exist('template_add_default')
        self.template.add_default(attr_name, attr_value)

    @check
    @log_func()
    def template_set_delimiter(self, dlm):
        self._check_template_exist('template_set_delimiter')
        self.template.set_delimiter(dlm)

    @check
    @log_func()
    def template_set_load_mode(self, load_mode):
        self._check_template_exist('template_set_load_mode')
        self.template.set_load_mode(load_mode)

    @check
    @log_func()
    def template_set_worker(self, worker_name):
        self._check_template_exist('template_set_worker')
        self.template.worker = worker_name

    @check
    @log_func()
    def clear_template(self):
        self.template = None

    @check
    @log_func()
    def create_model_using_template(self):
        self._check_template_exist('create_model_using_template')
        dic = self.template.compile()
        worker = self.template.get_worker()
        self.create_model(dic, worker)
        self.clear_template()

    @check
    @log_func()
    def modify_model_partition(self, model_name, modif_type, attr_name, attr_fmt=None, worker_name=None):
        self.logger.debug('modify_model_partition', worker_name=worker_name, model_name=model_name,modif_type=modif_type,
                          attr_name=attr_name)
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        worker.modify_partition(model_name, modif_type, attr_name, attr_fmt)
        self.meta.modify_data_model(worker_name, model_name, worker.get_model_header(model_name))

    @check
    @log_func()
    def modify_model_attribute(self, model_name, modif_type, attr_name, worker_name=None, **kwargs):
        self.logger.debug('modify_model_attribute', worker_name=worker_name, model_name=model_name, modif_type=modif_type,
                          attr_name=attr_name)
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        worker.modify_attribute(model_name, modif_type, attr_name, **kwargs)
        self.meta.modify_data_model(worker_name, model_name, worker.get_model_header(model_name))

    @check
    @log_func()
    def read_model_data(self, model_name, partition_filter='', data_filter='', selected_attrs=None, worker_name=None,
                        build_view_flg=None):
        self.logger.debug('read_model_data', model_name=model_name, partition_filter=partition_filter, data_filter=data_filter,
                          worker_name=worker_name, selected_attrs=selected_attrs, build_view_flg=build_view_flg)
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        if not partition_filter:
            parts = None
        else:
            parts = self.meta.filter
            parts.set_clause(partition_filter)
        part_list = worker.get_parts_list(model_name, parts)
        if not data_filter:
            fltr = None
        else:
            fltr = self.meta.filter
            fltr.set_clause(data_filter)
        data = worker.read_model_data(name=model_name, partitions_=part_list, filter_=fltr,
                                      selected=selected_attrs)
        if build_view_flg is None:
            build_view = self.meta.config[mm.DEFAULT_VIEW_TYPE_NAME]
            if build_view == mm.VIEW_DATA:
                build_view_flg = True
            else:
                build_view_flg = False
        if not isinstance(build_view_flg, bool):
            self.logger.error('read_model_data', 'build_view_flg: bool required, but {} found'.format(build_view_flg),
                              me.ModelManagerException)
            # raise me.ModelManagerException('Read model data Error', model_name, 'partition_filter \'{0}\', data_filter \'{1}\''.format(
            #     partition_filter, data_filter
            # ), 'incorrect value for build_view_flg: boolean value required, but {} found'.format(
            #     build_view_flg
            # ))
        view = mv.ModelView(model_name, data, self.log_generator, build_view_flg, worker.get_model_key(model_name),
                            worker.get_row_map(model_name), self.meta.get_model_hide_list(worker_name, model_name))
        return view

    @check
    @log_func()
    def write_model_data(self, model_name, list_str, attr_list=None, worker_name=None):
        self.logger.debug('write_model_data', worker_name=worker_name, model_name=model_name, attr_list=attr_list)
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        header = worker.get_model_header(model_name)
        load_type = header[mf.OPTIONS_KEY][mf.OPTION_LOAD_KEY]
        if load_type == mf.REPLACE_MODE:
            self.logger.note('write_model_data', 'Full data reloading mode')
            worker.truncate_model_data(model_name)
            brutal = True
        else:
            self.logger.note('write_model_data', 'Append data loading mode')
            brutal = False
        if isinstance(list_str, mv.ModelView):
            self.logger.note('write_model_data', 'Data source is ModelView object')
            attr_list = list_str.row_map
            tmp_list = list_str.convert_to_list()
            list_str = tmp_list.copy()
        worker.write_model_data(model_name, list_str, attr_list, brutal)

    @check
    @default_log
    def truncate_model_data(self, model_name, worker_name=None):
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        worker.truncate_model_data(model_name)

    @check
    @default_log
    def drop_model_partition(self, model_name, partition_filter='1=1', worker_name=None):
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        fltr = self.meta.filter
        fltr.set_clause(partition_filter)
        parts = worker.get_parts_list(model_name, fltr)
        worker.drop_partition(model_name, parts)

    @check
    @default_log
    def get_config(self, key):
        return self.meta.config[key]

    @check
    @default_log
    def set_config(self, key, value):
        self.meta.config[key] = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_model()


if __name__ == '__main__':
    b = ModelManager(r'D:\simple_test\test')
    b.logger.logger.close()
    b.create_models_from_script('test_file_parser.ddl')
    # b = ModelManager(r'D:\simple_test\test')
    b.add_worker('test_worker5')
    c = mv.ModelView('some_data', [[1,2,4],[1,2,5],[3,5,6]], b.log_generator, True, 3, ['num1', 'num2', 'key'])
    b.create_new_template('some_data')
    b.template_add_attr('key', 'int', True)
    b.template_add_attr('num1', 'int')
    b.template_add_attr('num2', 'int')
    b.template_set_worker('test_worker5')
    b.template_set_load_mode(mf.APPEND_MODE)
    b.create_model_using_template()
    b.write_model_data('some_data', c, worker_name='test_worker5')
    b.write_model_data('some_data', c, worker_name='test_worker5')
    print(c.data)
    d = b.read_model_data('some_data', worker_name='test_worker5', build_view_flg=False)
    print(d.data, d.row_map, d.logger.logger.is_closed())
    b.close_model()
    # b.create_new_template('sdfsd')

