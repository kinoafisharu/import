import sys
import os
import _pickle as pickle
import json

FILE = '/home/djapy/projects/Ivanovsandco/import/list_common_full_info.pickle'

def convert_dict_to_json():
    file = FILE
    with open(file, 'rb') as file_pkl, open('%s.json' % file, 'w') as fjson:
        data = pickle.load(file_pkl)
        json.dump(data, fjson, ensure_ascii=False, sort_keys=True, indent=4)


def main():
    if sys.argv[1] and os.path.isfile(sys.argv[1]):
        file_path = sys.argv[1]
        print("Processing %s ..." % file_path)
        convert_dict_to_json(file_path)
    else:
        print("Usage: %s abs_file_path" % (__file__))


if __name__ == '__main__':
    convert_dict_to_json()