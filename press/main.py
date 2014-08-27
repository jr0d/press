import logging

from configuration import configuration_from_file
from generators.layout import layout_from_config
from helpers.download import Download
from structure.exceptions import ConfigurationError

log = logging.getLogger(__name__)


class Press(object):
    def __init__(self, press_configuration, layout_only=False):
        self.configuration = press_configuration
        self.layout_only = layout_only

        log.info('Press initializing')

        log.info('Attempting to build Layout')

        self.layout = self._build_layout()

    def _build_layout(self):
        layout_config = self.configuration.get('layout')
        if not layout_config:
            raise ConfigurationError('Layout is missing')

        layout = layout_from_config(layout_config)

