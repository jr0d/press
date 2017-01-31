import json
import os
import yaml

SEARCH_PATHS = ['.', os.path.expanduser('~/.press'), '/etc/press']
ENVIRONMENT_FILENAME = 'environment.yaml'

environment_cache = {}


def configuration_from_yaml(data):
    return yaml.load(data)


def configuration_from_json(data):
    return json.loads(data)


def configuration_from_file(path, config_type='yaml'):
    with open(path) as fp:
        if config_type == 'yaml':
            return configuration_from_yaml(fp.read())
        if config_type == 'json':
            return configuration_from_json(fp.read())


def find_environment_configuration():
    for d in SEARCH_PATHS:
        filename = os.path.join(d, ENVIRONMENT_FILENAME)
        if os.path.isfile(filename):
            return filename


def set_environment_from_file(path=None):
    global environment_cache

    if not path:
        path = find_environment_configuration()

    try:
        set_environment(configuration_from_file(path, config_type='yaml'))
    except OSError:
        pass


def set_environment(environment):
    global environment_cache
    environment_cache.update(environment)
