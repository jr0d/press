import logging
from press.exceptions import ConfigurationError
from press.generators.layout import layout_from_config
from press.helpers import deployment
from press.layout.layout import MountHandler


log = logging.getLogger(__name__)


class LayoutMixin(object):
    mount_handler = None
    perform_teardown = True

    def __init__(self, press_configuration, deployment_root):
        self.__layout_configuration = press_configuration.get('layout')
        self.deployment_root = deployment_root

        if not self.__layout_configuration:
            raise ConfigurationError('Layout is missing!')

        self.layout = layout_from_config(self.__layout_configuration)

    def apply_layout(self):
        log.info('Applying layout')
        self.layout.apply()

    def mount_file_systems(self):
        self.mount_handler = MountHandler(self.deployment_root, self.layout)
        self.mount_handler.mount_physical()

    def mount_pseudo_file_systems(self):
        if self.mount_handler:
            self.mount_handler.mount_pseudo()

    def teardown(self):
        if self.mount_handler and self.perform_teardown:
            self.mount_handler.teardown()

    def write_fstab(self):
        log.info('Writing fstab')
        deployment.create_fstab(self.layout.generate_fstab(),
                                self.deployment_root)
