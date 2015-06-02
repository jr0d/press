# File is a POC

import logging
import pprint
import sys
import shutil

from traceback import format_exception

# Press imports
from configuration import global_defaults
from generators.chroot import target_mapping
from generators.post_target import target_mapping as new_target_mapping
from generators.image import downloader_generator
from generators.layout import layout_from_config
from helpers import deployment
from logger import setup_logging
from network.base import Network
from post.common import create_fstab
from plugins import init_plugins
from layout.exceptions import ConfigurationError, PressCriticalException
from layout.layout import MountHandler

log = logging.getLogger('press')


class Press(object):
    """
    The main orchestrator class, for v1
    """
    def __init__(self, press_configuration):
        """
        Parse the configuration and instansiate our classes.
        :param press_configuration:
        :return:
        """
        self.configuration = press_configuration
        self.target = global_defaults.press_target

        log.info('Press initializing', extra={'press_event': 'initializing'})

        layout_config = self.configuration.get('layout')
        if not layout_config:
            raise ConfigurationError('Layout is missing, this is kind of a big deal')

        self.layout = layout_from_config(layout_config)
        log.info('Layout generation successful')

        self.proxy_info = self.configuration.get('proxy_info')
        if self.proxy_info:
            log.info('Using proxy: %s' % pprint.pformat(self.proxy_info))

        self.image_configuration = self.configuration.get('image')
        if not self.image_configuration:
            raise ConfigurationError('There is no image defined, I have nothing to deploy')

        if 'file' in self.image_configuration:
            log.info('file path specified in configuration, not downloading')
            self.image_downloader = None
        else:
            self.image_downloader = downloader_generator(
                self.configuration.get('image'), self.target, self.proxy_info)

        if 'networking' in self.configuration:
            self.network = Network(self.target, self.configuration)
        else:
            self.network = None

        self.image_target = self.configuration['target']

        self.chroot_class = target_mapping.get(self.image_target)
        self.post_configuration_target = None

        if not self.chroot_class:
            # Temporary hack for testing
            self.post_configuration_target = new_target_mapping.get(self.image_target)

        self.mount_handler = None

    def burn_layout(self):
        """
        :return:
        """
        log.info('Applying layout to disk')
        self.layout.apply()

    def mount_file_systems(self):
        self.mount_handler = MountHandler(self.target, self.layout)
        self.mount_handler.mount_physical()

    def mount_pseudo_file_systems(self):
        self.mount_handler.mount_pseudo()

    def teardown(self):
        self.mount_handler.teardown()

    def download_and_validate_image(self):
        if not self.image_downloader:
            log.info('Copying image to target')
            shutil.copy(self.image_configuration['file'], self.target)
            return

        def our_callback(total, done):
            log.debug('Downloading: %.1f%%' % (float(done) / float(total) * 100))
        log.info('Starting download...')
        self.image_downloader.download(our_callback)
        log.info('done')
        if self.image_downloader.can_validate:
            log.info('Validating image')
            if not self.image_downloader.validate():
                raise PressCriticalException('Checksum validation error on image')
        else:
            log.info('Checksum validation on image is not possible')

    def extract_image(self):
        log.info('Extracting image and cleaning up')
        if self.image_downloader:
            self.image_downloader.extract(target_path=self.target)
            self.image_downloader.cleanup()
        else:
            deployment.tar_extract(self.image_configuration['file'], self.target)

    def write_fstab(self):
        log.info('Writing fstab')
        create_fstab(self.layout.generate_fstab(), self.target)

    def configure_network(self):
        if self.network:
            log.info('Configuring network')
            self.network.apply()
        else:
            log.warning('Network configuration is missing')

    def run_chroot(self):
        if self.chroot_class:
            log.info('Running chroot operations')
            obj = self.chroot_class(self.target, self.configuration, self.layout.disks)
            try:
                obj.apply()
            except:
                raise
            finally:
                if obj.init_completed:
                    obj.__exit__()
        else:
            log.warning('%s target is not currently supported. Sorry, Sam.' % self.image_target)

    def post_configuration(self):
        log.info('Running post configuration target')
        obj = self.post_configuration_target(self.configuration, self.layout.disks,
                                             self.target, global_defaults.staging_dir)
        obj.run()

    @staticmethod
    def __join_staging_dir():
        return global_defaults.press_target.rstrip('/') + '/' + global_defaults.staging_dir.lstrip('/')

    @staticmethod
    def create_staging_dir():
        deployment.recursive_makedir(Press.__join_staging_dir())

    @staticmethod
    def remove_staging_dir():
        deployment.recursive_remove(Press.__join_staging_dir())

    def crash_and_burn(self):
        """
        Place your head between your legs... and relax. You paid for the ticket,
        now take the damn ride.
        :return:
        """
        log.info('Installation is starting', extra={'press_event': 'deploying'})
        self.burn_layout()
        self.mount_file_systems()
        if self.image_downloader:
            log.info('Fetching image at %s' % self.image_downloader.url, extra={'press_event': 'downloading'})
        self.download_and_validate_image()
        self.extract_image()
        log.info('Configuring image', extra={'press_event': 'configuring'})
        self.write_fstab()
        # self.configure_network()
        self.mount_pseudo_file_systems()
        self.create_staging_dir()
        if self.chroot_class:
            self.run_chroot()
        if self.post_configuration_target:
            self.post_configuration()
        self.remove_staging_dir()
        log.info('Finished', extra={'press_event': 'complete'})


def entry_main(configuration, plugin_dir=None):
    setup_logging()
    log.debug('Logger initialized')
    init_plugins(configuration, plugin_dir)
    log.debug('Plugins initialized')
    try:
        press = Press(configuration)
    except Exception as e:
        traceback = format_exception(*sys.exc_info())
        log.error('Critical Error, %s, during initialization' % e, extra=dict(traceback=traceback,
                                                                              press_event='critical'))
        raise
    try:
        press.crash_and_burn()
    except Exception as e:
        traceback = format_exception(*sys.exc_info())
        log.error('Critical Error, %s, during deployment' % e, extra=dict(traceback=traceback,
                                                                          press_event='critical'))
        raise
    finally:
        if press.layout.committed:
            press.teardown()
