import json
import yaml


def configuration_from_yaml(data):
    return yaml.load(data)


def configuration_from_json(data):
    return json.loads(data)


def configuration_from_file(path, config_type='yaml'):
    with open(path) as fp:
        if config_type == 'yaml':
            return configuration_from_yaml(fp.read())
        if config_type == 'json':
            return configuration_from_yaml(fp.read())