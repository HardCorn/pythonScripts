import modelMeta as mm
import modelFile as mf
import osExtension as oe


test_dir = 'D:\\simple_test\\test\\'
mm.revalidate_path(test_dir, True)
# oe.extended_remove(test_dir, True, True)
mm.drop_all(test_dir, True)
meta_worker = mm.create_meta(test_dir)
print(meta_worker)
meta_path = mm.get_meta_path(test_dir)
# meta_worker = mf.ModelFileWorker(meta_path)
print(meta_worker.read_model_data(mm.MODELS_MODEL_NAME))
print(meta_worker.read_model_data(mm.WORKERS_MODEL_NAME))
print(meta_worker.read_model_data(mm.IDS_MODEL_NAME))
print(meta_worker.read_model_data(mm.CONFIG_MODEL_NAME))
