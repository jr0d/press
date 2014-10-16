## File is a POC

import logging
import pprint
import sys

from traceback import format_exception

# Press imports
from configuration import global_defaults
from generators.chroot import target_mapping
from generators.image import downloader_generator
from generators.layout import layout_from_config, generate_layout_stub
from logger import setup_logging
from network.base import Network
from post.common import create_fstab
from plugins import init_plugins
from structure.exceptions import ConfigurationError, PressCriticalException
from structure.layout import MountHandler
from structure.size import Size
from sysfs_info import has_efi

log = logging.getLogger('press')


class Press(object):
    """
    The main orchestrator class, for v1
    """
    @staticmethod
    def __add_bios_boot_partition(partition_table):
        """
        Hack. We meed to use a BIOS boot partition for booting gpt from BIOS.
        This will insert a 1MiB partition and flag the partition bios_grub.
        :return: Modified partition table structure
        """
        partitions = partition_table['partitions']
        if partitions:
            if not 'bios_grub' in partitions[0].get('flags', list()):
                log.info('Automatically inserting a BIOS boot partition')
                bios_boot_partition = dict(name='BIOS boot partition', size='1MiB', flags=['bios_grub'])
                partitions.insert(0, bios_boot_partition)
            else:
                log.info('BIOS boot partition seems to already be present, kudos!')
        partition_table['partitions'] = partitions
        return partition_table

    def __associate_disk_labels(self):
        """
        Hack. I didn't want to rewrite the partition generators, so I am going to read ahead into the
        configuration here and update the label field to gpt or msdos, based on associated
        disk size
        :return:
        """
        layout_configuration = self.configuration['layout']
        temp_layout = generate_layout_stub(layout_configuration)
        partition_tables = layout_configuration.get('partition_tables')
        log.info('Checking configuration for partition label types')
        for idx in xrange(len(partition_tables)):
            if partition_tables[idx].get('label'):
                log.info('Table %d is explicitly set to %s' % (idx, partition_tables[idx].get('label')))
                continue
            if partition_tables[idx]['disk'] == 'first':
                disk = temp_layout.unallocated[0]
            elif partition_tables[idx]['disk'] == 'any':
                size = Size(0)
                for partition in partition_tables[idx].get('partitions'):
                    if '%' not in partition['size']:
                        size += Size(partition['size'])
                disk = temp_layout.find_device_by_size(size)
            else:
                disk = temp_layout.find_device_by_ref(partition_tables[idx]['disk'])

            if not has_efi():
                if disk.size.over_2t:
                    log.info('%s is over 2.2TiB, using gpt' % disk.devname)
                    label = 'gpt'
                    if not layout_configuration.get('no_bios_boot_partition'):
                        # am I the first, possibly boot, disk?
                        if temp_layout.disks.keys().index(disk.devname) == 0:
                            partition_tables[idx] = self.__add_bios_boot_partition(partition_tables[idx])
                else:
                    log.info('%s is under 2.2TiB, using msdos' % disk.devname)
                    label = 'msdos'
            else:
                log.info('Booting in UEFI mode, using gpt partition table')
                label = 'gpt'

            partition_tables[idx]['label'] = label

        layout_configuration['partition_tables'] = partition_tables
        self.configuration['layout'].update(layout_configuration)

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

        self.__associate_disk_labels()

        self.layout = layout_from_config(layout_config)
        log.info('Layout generation successful')

        self.proxy_info = self.configuration.get('proxy_info')
        if self.proxy_info:
            log.info('Using proxy: %s' % pprint.pformat(self.proxy_info))

        self.image_configuration = self.configuration.get('image')
        if not self.image_configuration:
            raise ConfigurationError('There is no image defined, I have nothing to deploy')

        self.image_downloader = downloader_generator(
            self.configuration.get('image'), self.target, self.proxy_info)

        if 'networking' in self.configuration:
            self.network = Network(self.target, self.configuration)
        else:
            self.network = None

        self.image_target = self.configuration['target']

        self.chroot_class = target_mapping.get(self.image_target)

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
        log.info('Extracting image...')
        self.image_downloader.extract(target_path=self.target)
        log.info('Removing image archive')
        self.image_downloader.cleanup()

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

    def crash_and_burn(self):
        """
        Place your head between your legs... and relax. You paid for the ticket,
        now take the damn ride.
        :return:
        """
        log.info('Installation is starting', extra={'press_event': 'deploying'})
        self.burn_layout()
        self.mount_file_systems()
        log.info('Fetching image at %s' % self.image_downloader.url, extra={'press_event': 'downloading'})
        self.download_and_validate_image()
        self.extract_image()
        log.info('Configuring image', extra={'press_event': 'configuring'})
        self.write_fstab()
        self.configure_network()
        self.mount_pseudo_file_systems()
        self.run_chroot()
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


