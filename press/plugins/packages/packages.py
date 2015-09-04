import logging

from press.targets.registration import register_extension
from press.targets.target_base import TargetExtension

log = logging.getLogger('press.plugins.package')


class PackageExtension(TargetExtension):
    __extends__ = 'linux'
    __configuration__ = {}

    def run(self):
        packages = self.__configuration__.get('packages', [])
        log.debug('Rackspace packages: %s' % ', '.join(packages))
        missing = self.target.packages_missing(packages)
        self.target.install_packages(missing)


def plugin_init(configuration):
    log.info('Registering Rackspace Package Extension')
    if configuration.get('packages'):
        PackageExtension.__configuration__ = configuration
        register_extension(PackageExtension)
    else:
        log.info('Packages plugin enabled buy no packages are specified')
