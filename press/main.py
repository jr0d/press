import logging

from configuration import configuration_from_file, global_defaults
from generators.image import downloader_generator
from generators.layout import layout_from_config
from network.base import Network
from structure.exceptions import ConfigurationError

log = logging.getLogger(__name__)


class Press(object):
    """
    The main orchestrator class
    """
    def __init__(self, press_configuration):
        self.configuration = press_configuration
        self.target = global_defaults.press_target

        log.info('Press initializing')

        log.info('Attempting to generate Layout')

        layout_config = self.configuration.get('layout')
        if not layout_config:
            raise ConfigurationError('Layout is missing, this is kind of a big deal')

        self.layout = layout_from_config(layout_config)

        log.info('Layout generation successful')

        self.proxy_info = self.configuration.get('proxy_info')
        if self.proxy_info:
            log.debug('Using proxy: %s' % self.proxy_info)

        self.image_configuration = self.configuration.get('image')
        if not self.image_configuration:
            raise ConfigurationError('The is no image defined, I have nothing to deploy')

        self.image_downloader = downloader_generator(
            self.configuration.get('image'), self.target, self.proxy_info)

        self.network_configuration = self.configuration.get('network')
        if self.network_configuration:
            self.network = Network(self.target, self.network_configuration)


