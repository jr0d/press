from pprint import pprint
from press.configuration import configuration_from_file

config_file = 'doc/yaml/simple.yaml'

configuration = configuration_from_file(config_file)

pprint(configuration)