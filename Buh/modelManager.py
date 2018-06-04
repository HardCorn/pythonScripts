import modelExceptions as me
import modelUtility as mu
import osExtension as oe
import modelMeta as mm
import modelFile as mf
import ModelTemplate as mt


class ModelManager:
    def __init__(self, model_directory):
        oe.revalidate_path(model_directory, True)
        self.meta = mm.ModelMeta(model_directory)
        self.template = None

    def clear_template(self):
        self.template = None

    def create_new_model(self, model_name, model_worker):
        if self.template:
            self.clear_template()
        self.template = mt.ModelTemplate(model_name, worker=model_worker)