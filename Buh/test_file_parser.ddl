worker Main
name test_model1
attrs (
fld1 int key default 1,
fld2 str hide default 'Nothing wrong'
)
partition (fld2 None,);
worker Main
name test_model2
attr key1 int
attr fld3 date
attr fld4 dttm
hide (fld3, fld4)
key key1
partition (fld3 'YYYYMMDD', fld4 'YYYYMM')
default (fld3 '2018-04-12 00:00:00.000000', key1 4)