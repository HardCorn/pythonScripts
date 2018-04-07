import modelMeta as mm
import modelFile as mf
import osExtension as oe
import dates as dt
import modelUtility as mu


test_dir = 'D:\\simple_test\\test\\'
oe.revalidate_path(test_dir, True)
# oe.extended_remove(test_dir, True, True)
mm.drop_all(test_dir, True)
# meta_worker = mm.create_meta(test_dir)
# print(meta_worker)
# meta_path = mm.get_meta_path(test_dir)
# meta_worker = mf.ModelFileWorker(meta_path)
# print(meta_worker.read_model_data(mm.MODELS_MODEL_NAME))
# print(meta_worker.read_model_data(mm.WORKERS_MODEL_NAME))
# print(meta_worker.read_model_data(mm.IDS_MODEL_NAME))
# print(meta_worker.read_model_data(mm.CONFIG_MODEL_NAME))
meta = mm.ModelMeta(test_dir)
king = meta.add_data_worker('Stiven_king')
attrs_dict = {'key_field': 'str',
              'info_field1': 'str',
              'info_field2': 'int',
              'date_field': 'date'}
defaults_dict = {'key_field': 'no_sense_string',
                 'info_field1': 'i\'m a monkey',
                 'info_field2': 42,
                 'date_field': dt.date(2015, 12, 29)}
partition_dict = {'date_field': 'YYYYMM',
                  'info_field2': None}
king.create_model('Cristine', attrs_dict, 'key_field', partition_dict, delim='|^|', defaults=defaults_dict)
header = king.get_model_header('Cristine')
meta.add_data_model('Stiven_king', 'Cristine', header)
print(meta.worker.read_model_data(mm.WORKERS_MODEL_NAME))
print(meta.worker.read_model_data(mm.MODELS_MODEL_NAME))
print(meta.worker.read_model_data(mm.IDS_MODEL_NAME))
print(meta.worker.read_model_data(mm.CONFIG_MODEL_NAME))
print(meta.config)
meta.drop_data_model('Stiven_king', 'Cristine')
print(meta.worker.read_model_data(mm.WORKERS_MODEL_NAME))
print(meta.worker.read_model_data(mm.MODELS_MODEL_NAME))
print(meta.worker.read_model_data(mm.IDS_MODEL_NAME))
print(meta.worker.read_model_data(mm.CONFIG_MODEL_NAME))
meta.drop_data_worker('Stiven_king')
print(meta.worker.read_model_data(mm.WORKERS_MODEL_NAME))
print(meta.worker.read_model_data(mm.MODELS_MODEL_NAME))
print(meta.worker.read_model_data(mm.IDS_MODEL_NAME))
print(meta.worker.read_model_data(mm.CONFIG_MODEL_NAME))
fl = mu.Filter()
fl.set_clause('worker_name = \'Main\'')
dt = meta.worker.read_model_data(mm.WORKERS_MODEL_NAME, filter_=fl)
print(dt)