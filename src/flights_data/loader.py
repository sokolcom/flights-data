import yaml


class ConfigLoader(yaml.YAMLObject):
    yaml_tag = '!conn_db'

    @classmethod
    def from_yaml(cls, loader, node):
        value = loader.construct_mapping(node)
        return ConfigLoader(**value)

    def __init__(self, dbname=None, user=None, password=None, host="localhost", port=5432):
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port
 
    def __call__(self):
        return {
            "database": self._dbname,
            "user": self._user,
            "password": self._password, 
            "host": self._host,
            "port": self._port
        }


def load_config(filepath):
    params = None
    with open(filepath, "r") as config_file:
        connector = yaml.load(config_file, Loader=yaml.FullLoader)
        params = connector()
    return params



class AuthorizedLoader(yaml.YAMLObject):
    yaml_tag = '!granted'

    @classmethod
    def from_yaml(cls, loader, node):
        value = loader.construct_mapping(node)
        return AuthorizedLoader(**value)

    def __init__(self, tokens=()):
        self._tokens = tokens
 
    def __call__(self):
        return {
            "tokens": self._tokens,
        }

def load_auth_users(filepath):
    params = None
    with open(filepath, "r") as fin:
        connector = yaml.load(fin, Loader=yaml.FullLoader)
        params = connector()
    return params