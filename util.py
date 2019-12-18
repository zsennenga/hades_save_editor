import os

import data


def load_data_file_as_binary(filename):
    with open(get_path_to_data_file(filename), mode='rb') as file_:
        return file_.read()


def get_path_to_data_file(filename):
    return os.path.join(os.path.basename(data.__path__[0]), filename)
