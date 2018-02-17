import os
import tempfile
import sys
import json
import argparse
import functools

def to_json(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        return json.dumps(f(*args, **kwargs))
    return wrapped


@to_json
def get_data():
  return {
    'data': 'ываыва'
  }



def read(file_path):
    res = ''
    with open(file_path, 'r') as f:
        res = f.read()
        if len(res) != 0:
            res = json.loads(res)
    result = dict(res)
    # print(result)
    return result


def write(file_path, store_data):
    tempstr = ''
    with open(file_path, 'w')as f:

        if len(store_data) != 0:
            tempstr = json.dumps(store_data)
        f.write(tempstr)
    # print(tempstr)

def add(store_data, key, val):
    ln = 0
    temp_val = {0: val}
    if key in store_data:
        temp_val = store_data[key]
        ln = len(temp_val)
        temp_val[ln] = val
    store_data[key] = temp_val
    # print(store_data)


def get_val(store_data, key):
    res =  {}
    result = ''
    if key in store_data:
        res = store_data[key]


    for tmp in sorted(res):
        if tmp == "0":
            result = res[tmp]
        else:
            result = result + ', ' + res[tmp]
    # print(result)
    return result


if __name__ == "__main__":
    print (get_data())
    args = argparse.ArgumentParser()
    args.add_argument("--key", help = "access key")
    args.add_argument("--value", help = "value of the key")
    args = args.parse_args()
    storage_path = os.path.join(tempfile.gettempdir(), 'storage.data')
    if not args.key:
        print('by, world')

    else:
        data = read(storage_path)

        if args.value:
            add(data, args.key, args.value)
            write(storage_path, data)

        else:
            print(get_val(data, args.key))



    """
    if len(sys.argv) == 2:
        result = ''
        splitter = ''
        with open(storage_path, 'r') as f:
            temp_str = f.readline().strip()
            #print(temp_str)
            while temp_str:
                temp_res = f.readline().strip()
                #print(temp_res, splitter)
                if temp_str == sys.argv[1]:
                    #print(result, temp_res)
                    result = result + splitter + temp_res.strip()
                    splitter = ', '
                temp_str = f.readline().strip()
        print(result)

    elif len(sys.argv) == 3:
        with open(storage_path, 'a') as f:
            #f.write(str(sys.argv[1]) +'\r\n' + str(sys.argv[2]))
            f.write(str(sys.argv[1]) + '\n')
            f.write(str(sys.argv[2]) + '\n')

    else:
        print('by world')"""