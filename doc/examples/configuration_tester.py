from press.configuration import configuration_from_file
from press.generators.layout import layout_from_config
from press.logger import setup_logging

setup_logging()

config_file = 'doc/yaml/simple.yaml'

configuration = configuration_from_file(config_file)

layout_config = configuration['layout']

layout = layout_from_config(layout_config)

layout.apply()

print(layout.generate_fstab())
