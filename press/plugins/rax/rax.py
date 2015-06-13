import logging
import time

from press.helpers import deployment
from press.targets.registration import register_extension
from press.targets.target_base import TargetExtension

log = logging.getLogger('press.plugins.rax')


class RaxExtension(TargetExtension):
    __extends__ = 'linux'
    __configuration__ = {}

    def create_rackspace_directories(self):
        log.info('Creating /boot/.rackspace')
        deployment.recursive_makedir(self.join_root('/boot/.rackspace'))
        log.info('Creating /root/.rackspace')
        deployment.recursive_makedir(self.join_root('/root/.rackspace'))

    def create_file(self, name, data):
        path = '/root/.rackspace/' + name
        log.info('Creating %s' % path)
        deployment.write(self.join_root(path), '%s\n' % data)

    def create_cookies(self):
        rax_configuration = self.get('rax')
        for k, v in rax_configuration.items():
            self.create_file(k, v)
        self.create_file('kick_date', time.ctime())

    def get(self, k):
        return self.__configuration__.get(k)

    def run(self):
        log.info('Creating COOOOOKIEEESSSSSS NOM nom NOM nom!')
        self.create_rackspace_directories()
        self.create_cookies()


def plugin_init(configuration):
    log.info('Registering Rackspace Support Extension')
    RaxExtension.__configuration__ = configuration
    register_extension(RaxExtension)
