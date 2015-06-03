import logging

# Press imports
from .configuration import global_defaults
from .generators.chroot import target_mapping
from .generators.post_target import target_mapping as new_target_mapping
from .generators.image import downloader_generator
from .generators.layout import layout_from_config, generate_layout_stub
from .helpers import deployment
from .logger import setup_logging
from .network.base import Network
from .plugins import init_plugins
from .layout.exceptions import ConfigurationError, PressCriticalException
from .layout.layout import MountHandler
from .layout.size import Size
from .sysfs_info import has_efi

log = logging.getLogger('press')


class Press(object):
    """

    """
    def generate_layout(self):
        layout_config = self.configuration.get('layout')
        if not layout_config:
            raise ConfigurationError('Layout is missing')
        self.layout = layout_from_config(layout_config)

    def global_proxy(self):
        pi = self.configuration.get('proxy_info')
        if pi:
            log.debug('Using proxy, %s, where possible.' % pi)
        self.proxy_info = pi

    def set_downloader(self):
        self.downloader = downloader_generator(self.image_configuration,
                                               self.deployment_root,
                                               self.proxy_info)

    def __init__(self, press_configuration,
                 deployment_root='/mnt/press',
                 staging_dir='/.press'
                 ):
        """
        :param press_configuration:
        :param deployment_root:
        :param staging_dir:
        :return:
        """
        self.configuration = press_configuration
        self.deployment_root = deployment_root.rstrip('/')
        self.staging_dir = staging_dir

        log.info('Press initializing', extra={'press_event': 'initializing'})

        self.layout = None
        self.proxy_info = None
        self.image_target = None
        self.downloader = None
        self.generate_layout()

    def download_image(self):
        def our_callback(total, done):
            log.debug('Downloading: %.1f%%' % (float(done) / float(total) * 100))

        log.info('Starting Download...')
        self.downloader.download(our_callback)
        log.info('done')

    def validate_image(self):

    @property
    def image_configuration(self):
        return self.configuration.get('image')

    @property
    def full_staging_dir(self):
        return self.deployment_root + '/' + self.staging_dir.lstrip('/')

    def create_staging_dir(self):
        deployment.recursive_makedir(self.full_staging_dir)

    def remove_staging_dir(self):
        deployment.recursive_remove(self.full_staging_dir)


