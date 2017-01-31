from __future__ import absolute_import

import logging

# Press imports
from press.configuration.util import environment_cache
from press.generators.image import ImageMixin
from press.helpers import deployment
from press.helpers.kexec import kexec
from press.layout.layout_mixin import LayoutMixin
from press.targets import VendorRegistry
from press.targets.registration import apply_extension, target_extensions
from press.hooks.hooks import run_hooks


log = logging.getLogger('press')


class Press(LayoutMixin, ImageMixin):
    """
    Primary orchestration class for press
    """
    def __init__(self, press_configuration):
        """
        :param press_configuration:
        :param deployment_root:
        :param staging_dir:
        :return:
        """
        self.configuration = press_configuration
        self.deployment_root = environment_cache.get('press', {}).get('deployment_root', '/mnt/press')
        self.staging_dir = environment_cache.get('press', {}).get('staging_directory', '/.press')

        LayoutMixin.__init__(self, press_configuration, self.deployment_root)
        ImageMixin.__init__(self, press_configuration, self.deployment_root)

        log.info('Press initializing', extra={'press_event': 'initializing'})

        self.image_target = press_configuration.get('target')
        self.post_configuration_target = VendorRegistry.targets.get(self.image_target)
        run_hooks("post-press-init", self.configuration)

    @staticmethod
    def run_extensions(obj):
        if not target_extensions:
            log.debug('There are no extensions registered')
        for extension in target_extensions:
            if apply_extension(extension, obj):
                log.info('Running Extension: %s' % extension.__name__)
                extension(obj).run()

    def post_configuration(self):
        if not self.post_configuration_target:
            log.info('Target: %s is not supported' % self.image_target)
            return

        log.info('Running post configuration target')
        obj = self.post_configuration_target(self.configuration,
                                             self.layout,
                                             self.deployment_root,
                                             self.staging_dir)
        self.write_fstab()
        self.mount_pseudo_file_systems()
        run_hooks("pre-create-staging", self.configuration)
        self.create_staging_dir()
        run_hooks("pre-target-run", self.configuration)
        obj.run()
        run_hooks("pre-extensions", self.configuration)
        self.run_extensions(obj)
        run_hooks("post-extensions", self.configuration)
        self.remove_staging_dir()
        if hasattr(obj, 'write_resolvconf'):
            obj.write_resolvconf()

    @property
    def full_staging_dir(self):
        return self.deployment_root + '/' + self.staging_dir.lstrip('/')

    def create_staging_dir(self):
        deployment.recursive_makedir(self.full_staging_dir)

    def remove_staging_dir(self):
        deployment.recursive_remove(self.full_staging_dir)

    def run(self):
        log.info('Installation is starting', extra={'press_event': 'deploying'})
        run_hooks("pre-apply-layout", self.configuration)
        self.apply_layout()
        if self.image_configuration:
            run_hooks("pre-mount-fs", self.configuration)
            self.mount_file_systems()
            log.info('Fetching image at %s' % self.imagefile.url,
                     extra={'press_event': 'downloading'})
            run_hooks("pre-image-ops", self.configuration)
            self.run_image_ops()
            log.info('Configuring image', extra={'press_event': 'configuring'})
            run_hooks("pre-post-config", self.configuration)
            self.post_configuration()

        else:
            log.info('Press configured in layout only mode, finishing up.')

        log.info('Finished', extra={'press_event': 'complete'})

        # Experimental
        kexec_config = self.configuration.get('kexec')
        if kexec_config:
            self.perform_teardown = False
            kexec(layout=self.layout, **kexec_config)
