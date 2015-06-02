import logging

# Press imports
from press.configuration import global_defaults
from press.generators.chroot import target_mapping
from press.generators.post_target import target_mapping as new_target_mapping
from press.generators.image import downloader_generator
from press.generators.layout import layout_from_config, generate_layout_stub
from press.helpers import deployment
from press.logger import setup_logging
from press.network.base import Network
from press.post.common import create_fstab
from press.plugins import init_plugins
from press.layout.exceptions import ConfigurationError, PressCriticalException
from press.layout.layout import MountHandler
from press.layout.size import Size
from press.sysfs_info import has_efi

log = logging.getLogger('press')


class Press(object):
    """

    """

    def __init__(self, target_configuration,
                 deployment_root='/mnt/press',
                 staging_dir='/.press',
                 ):
        """
        :param target_configuration:
        :param deployment_target:
        :param staging_dir:
        :return:
        """
        self.target_configuration = target_configuration
        self.deployment_root = deployment_root