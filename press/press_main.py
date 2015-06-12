import logging

# Press imports
from press.layout.layout_mixin import LayoutMixin
from press.generators.image import ImageMixin
from press.helpers import deployment
from press.targets import VendorRegistry

log = logging.getLogger('press')


class Press(LayoutMixin, ImageMixin):
    """

    """
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

        LayoutMixin.__init__(self, press_configuration, deployment_root)
        ImageMixin.__init__(self, press_configuration, deployment_root)

        log.info('Press initializing', extra={'press_event': 'initializing'})

        self.image_target = press_configuration.get('target')
        # Replaced once dynamic target discovery is implemented
        self.post_configuration_target = VendorRegistry.targets.get(self.image_target)

    def post_configuration(self):
        if not self.post_configuration_target:
            log.info('Target: %s is not supported' % self.image_target)
            return

        log.info('Running post configuration target')
        obj = self.post_configuration_target(self.configuration,
                                             self.layout.disks,
                                             self.deployment_root,
                                             self.staging_dir)
        self.write_fstab()
        self.mount_pseudo_file_systems()
        self.create_staging_dir()
        obj.run()
        self.remove_staging_dir()

    @property
    def full_staging_dir(self):
        return self.deployment_root + '/' + self.staging_dir.lstrip('/')

    def create_staging_dir(self):
        deployment.recursive_makedir(self.full_staging_dir)

    def remove_staging_dir(self):
        deployment.recursive_remove(self.full_staging_dir)

    def run(self):
        log.info('Installation is starting', extra={'press_event': 'deploying'})
        self.apply_layout()
        if self.image_configuration:
            self.mount_file_systems()
            log.info('Fetching image at %s' % self.imagefile.url,
                     extra={'press_event': 'downloading'})
            self.run_image_ops()
            log.info('Configuring image', extra={'press_event': 'configuring'})
            self.post_configuration()
        else:
            log.info('Press configured in layout only mode, finishing up.')
        log.info('Finished', extra={'press_event': 'complete'})

