import logging

from press.targets.registration import register_extension
from press.targets.target_base import TargetExtension

log = logging.getLogger('press.plugins.rax')


class RaxExtension(TargetExtension):
    __extends__ = 'linux'
    __configuration__ = {}

    def create_rackspace_directories
    def run(self):
        log.info('HELLO World!!!')


def plugin_init(configuration):
    log.info('Registering Rackspace Support Extension')
    RaxExtension.__configuration__ = configuration
    register_extension(RaxExtension)
