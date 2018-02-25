import modelMeta as mm
import modelFile as mf
import os


test_dir = 'C:\\simple_test\\test\\'
# os.remove(test_dir)
meta_worker = mm.create_meta(test_dir)
print(meta_worker)
meta_path = mm.get_meta_path(test_dir)
meta_worker = mf.ModelFileWorker(meta_path)
print(meta_worker.read_model_data(mm.MODELS_MODEL_NAME))
print(meta_worker.read_model_data(mm.WORKERS_MODEL_NAME))
print(meta_worker.read_model_data(mm.IDS_MODEL_NAME))
