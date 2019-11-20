"""
CreateTime    : 2019/6/4 22:26
Author        : X
Filename      : tools.py
"""
import os
import json
from hashlib import md5
from settings import BASE_DIR


def load_config(file_name):
    """
    Load json config file.
    :param file_name: str, the name of config file
    :return: json
    """
    file_path = os.path.join(BASE_DIR, "etc", file_name)
    with open(file_path) as config:
        return json.load(config)


def get_hash_code(name):
    """get hash code by string"""
    hasher = md5(name.encode('utf-8'))
    return hasher.hexdigest()