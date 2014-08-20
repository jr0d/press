import yaml


class Configuration(object):
    def __init__(self, config_dict):
        self.__dict__.update(config_dict)


def configuration_from_yaml(data):
    return yaml.load(data)


def configuration_from_file(path, config_type='yaml'):
    with open(path) as fp:
        if config_type == 'yaml':
            return configuration_from_yaml(fp.read())