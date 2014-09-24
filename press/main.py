import logging
import pprint

from configuration import configuration_from_file, global_defaults
from generators.chroot import target_mapping
from generators.image import downloader_generator
from generators.layout import layout_from_config, generate_layout_stub
from logger import setup_logging
from network.base import Network
from plugins import init_plugins
from structure.exceptions import ConfigurationError
from structure.size import Size

log = logging.getLogger('press')


class Press(object):
    """
    The main orchestrator class, for v1
    """

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

            if disk.size.over_2t:
                log.info('%s is over 2.2TiB, using gpt' % disk.devname)
                label = 'gpt'
            else:
                log.info('%s is under 2.2TiB, using msdos' % disk.devname)
                label = 'msdos'

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

        log.info('Press initializing')

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
            raise ConfigurationError('The is no image defined, I have nothing to deploy')

        self.image_downloader = downloader_generator(
            self.configuration.get('image'), self.target, self.proxy_info)

        if 'network' in self.configuration:
            self.network = Network(self.target, self.configuration)
        else:
            self.network = None

        self.chroot_class = target_mapping.get(self.configuration['target'])

    def download_and_verify_image(self):
        pass

    def burn(self):
        """
        Got time.
        :return:
        """
        pass


def entry():
    pass


if __name__ == '__main__':
    setup_logging()
    config = configuration_from_file('doc/yaml/simple.yaml')
    init_plugins(config)
    press = Press(config)
    print press.layout
    print press.chroot_class.__name__
