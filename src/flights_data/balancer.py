import os.path as path
from random import random
from hashlib import sha256

import peewee as orm
from flask import request

from .loader import load_config


YAML_CONFIG_MASTER = path.abspath("flights_data/data/conn_master.yaml")
YAML_CONFIG_SLAVE = path.abspath("flights_data/data/conn_slave.yaml")
YAML_AUTHORIZED_USERS = path.abspath("flights_data/data/authorized.yaml")


def connect_db(request_path):
    params = None
    if request.method == "GET":
        params = load_config(YAML_CONFIG_SLAVE)
        hash = sha256(f"{request_path}{random()}".encode(encoding="utf-8")).digest()[0]  # f"{random()}".encode()
        params["host"] = params["host"][hash % len(params["host"])] 
    else:
        params = load_config(YAML_CONFIG_MASTER)
    
    # params = load_config(YAML_CONFIG_MASTER)
    return orm.PostgresqlDatabase(**params)
