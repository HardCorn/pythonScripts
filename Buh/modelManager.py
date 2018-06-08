import modelExceptions as me
import modelUtility as mu
import osExtension as oe
import modelMeta as mm
import modelFile as mf
import ModelTemplate as mt
import ModelView as mv


class ModelManager:

    TNone = mt.ModelTemplate.TNone

    def __init__(self, model_directory, recreate_flg=False):
        self.model_directory = model_directory
        if recreate_flg:
            self.drop_all()
        oe.revalidate_path(model_directory, True)
        self.meta = mm.ModelMeta(model_directory)
        self.template = None

    def add_worker(self, worker_name):
        self.meta.add_data_worker(worker_name)

    def drop_worker(self, worker_name):
        if worker_name not in self.meta.data_workers:
            raise me.ModelManagerException('Drop worker error', worker_name, 'worker does not exist!')
        path = mm.get_worker_path(self.model_directory, worker_name)
        oe.extended_remove(path, True)
        self.meta.drop_data_worker(worker_name)

    def drop_all(self):
        oe.extended_remove(self.model_directory, True)

    def _revalidate_worker(self, worker_name):
        if worker_name is None:
            worker_name = self.meta.config[mm.DEFAULT_WORKER_NAME]
        return worker_name


    def create_model(self, model_dictionary, model_worker=None):
        model_worker = self._revalidate_worker(model_worker)
        if 'delim' not in model_dictionary:
            model_dictionary['delim'] = self.meta.config[mm.DEFAULT_DELIMITER_NAME]
        if 'load_mode' not in model_dictionary:
            model_dictionary['load_mode'] = self.meta.config[mm.DEFAULT_MODEL_LOAD_MODE]
        name = model_dictionary['name']
        if model_worker not in self.meta.data_workers:
            raise me.ModelManagerException('Create model error', name, 'worker \'{}\' does not exist'.format(model_worker))
        worker = self.meta.data_workers[model_worker]
        worker.create_model(**model_dictionary)
        self.meta.add_data_model(model_worker, name, worker.get_model_header(name))

    def create_model_from_json(self, file_path):
        dic = mt.create_models_from_file(file_path, True)
        if 'worker' in dic:
            worker = dic['worker']
        else:
            worker = None
        del dic['worker']
        self.create_model(dic, worker)

    def create_models_from_script(self, file_path):
        model_templates = mt.create_models_from_file(file_path)
        for each in model_templates:
            self.create_model(each.compile(), each.get_worker())

    def create_new_template(self, model_name, model_attrs=None, model_partition=None, model_key=None, model_delimiter=None,
                         attr_defaults=None, model_worker=None, hide_attrs=None, load_mode=None):
        if self.template is not None:
            raise me.ModelManagerException('Create new template', model_name, 'Template is not empty! ({})'.format(self.template))
        self.template = mt.ModelTemplate(model_name, model_attrs, model_partition, model_key, model_delimiter,
                                         attr_defaults, model_worker, hide_attrs, load_mode)

    def _check_template_exist(self, err_msg):
        if self.template is None:
            raise me.ModelManagerException(err_msg, 'there are no template to modify')

    def template_add_attr(self, attr_name, attr_type, key=False, partition=TNone, default=TNone, hide=False):
        self._check_template_exist('Add attribute to template Error')
        self.template.add_attr(attr_name, attr_type, key, partition, default, hide)

    def template_add_partition(self, attr_name, attr_fmt):
        self._check_template_exist('Add partition to template Error')
        self.template.add_partition(attr_name, attr_fmt)

    def template_set_key(self, key_attr):
        self._check_template_exist('Set key to template Error')
        self.template.set_key(key_attr)

    def template_hide_attr(self, attr_name):
        self._check_template_exist('Hide template attribute Error')
        self.template.hide_attr(attr_name)

    def template_add_default(self, attr_name, attr_value):
        self._check_template_exist('Add default values to template Error')
        self.template.add_default(attr_name, attr_value)

    def template_set_delimiter(self, dlm):
        self._check_template_exist('Set delimiter to template Error')
        self.template.set_delimiter(dlm)

    def template_set_load_mode(self, load_mode):
        self._check_template_exist('Set loading mode to template Error')
        self.template.set_load_mode(load_mode)

    def template_set_worker(self, worker_name):
        self._check_template_exist('Set template worker Error')
        self.template.worker = worker_name

    def clear_template(self):
        self.template = None

    def create_model_using_template(self):
        self._check_template_exist('Creating model using template')
        dic = self.template.compile()
        worker = self.template.get_worker()
        self.create_model(dic, worker)
        self.clear_template()

    def modify_model_partition(self, model_name, modif_type, attr_name, attr_fmt=None, worker_name=None):
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        worker.modify_partition(model_name, modif_type, attr_name, attr_fmt)
        self.meta.modify_data_model(worker_name, model_name, worker.get_model_header(model_name))

    def modify_model_attribute(self, model_name, modif_type, attr_name, worker_name=None, **kwargs):
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        worker.modify_attribute(model_name, modif_type, attr_name, **kwargs)
        self.meta.modify_data_model(worker_name, model_name, worker.get_model_header(model_name))

    def read_model_data(self, model_name, partition_filter='', data_filter='', selected_attrs=None, worker_name=None,
                        build_view_flg=None):
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        if not partition_filter:
            partition_filter = '1=1'
        if not data_filter:
            data_filter = '1=1'
        self.meta.filter.set_clause(partition_filter)
        part_list = worker.get_parts_list(model_name, self.meta.filter)
        self.meta.filter.set_clause(data_filter)
        data = worker.read_model_data(name=model_name, partitions_=part_list, filter_=self.meta.filter,
                                      selected=selected_attrs)
        if build_view_flg is None:
            build_view = self.meta.config[mm.DEFAULT_VIEW_TYPE_NAME]
            if build_view == mm.VIEW_DATA:
                build_view_flg = True
            else:
                build_view_flg = False
        if not isinstance(build_view_flg, bool):
            raise me.ModelManagerException('Read model data Error', model_name, 'partition_filter \'{0}\', data_filter \'{1}\''.format(
                partition_filter, data_filter
            ), 'incorrect value for build_view_flg: boolean value required, but {} found'.format(
                build_view_flg
            ))
        view = mv.ModelView(model_name, data, build_view_flg, worker.get_model_key(model_name), worker.get_row_map(model_name),
                            self.meta.get_model_hide_list(worker_name, model_name))
        return view

    def write_model_data(self, model_name, list_str, attr_list=None, worker_name=None):
        worker_name = self._revalidate_worker(worker_name)
        worker = self.meta.data_workers[worker_name]
        header = worker.get_model_header(model_name)
        load_type = header[mf.OPTIONS_KEY][mf.OPTION_LOAD_KEY]
        if load_type == mf.REPLACE_MODE:
            worker.truncate_model_data(model_name)
            brutal = True
        else:
            brutal = False
        if isinstance(list_str, mv.ModelView):
            attr_list = list_str.row_map
            tmp_list = list_str.convert_to_list()
            list_str = tmp_list.copy()
        worker.write_model_data(model_name, list_str, attr_list, brutal)


if __name__ == '__main__':
    # b = ModelManager(r'C:\simple_test\test', True)
    # b.create_models_from_script('test_file_parser.ddl')
    b = ModelManager(r'C:\simple_test\test')
    b.add_worker('test_worker5')
    c = mv.ModelView('some_data', [[1,2,4],[1,2,5],[3,5,6]], True, 3, ['num1', 'num2', 'key'])
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
    print(d.data, d.row_map)
