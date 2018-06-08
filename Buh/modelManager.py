import modelExceptions as me
import modelUtility as mu
import osExtension as oe
import modelMeta as mm
import modelFile as mf
import ModelTemplate as mt


class ModelManager:
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

    def create_model(self, model_dictionary, model_worker=None):
        if model_worker is None:
            model_worker = self.meta.config[mm.DEFAULT_WORKER_NAME]
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
            self.create_model(each.compile(), each.worker)


if __name__ == '__main__':
    b = ModelManager(r'C:\simple_test\test', True)
    b.create_models_from_script('test_file_parser.ddl')

