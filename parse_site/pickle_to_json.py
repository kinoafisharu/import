import sys
import os
import _pickle as pickle
import json
from collections import defaultdict


def get_files_in_path(path='/home/djapy/projects/Ivanovsandco/import/storage'):
    intermediate_list = []
    for root, dirs, files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            intermediate_list.append(file_path)
    return intermediate_list


def convert_dict_to_json(file):
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
    list_pickle_files = get_files_in_path()
    for pickle_files in list_pickle_files:
        convert_dict_to_json(pickle_files)
