import logging
import os
from press.helpers import deployment
from press.targets.target_base import TargetExtension


log = logging.getLogger('press.plugins.server_management')


class VMWareTools(TargetExtension):
    __extends__ = 'ubuntu_1404'

    def run(self):
        log.info('Install vmware tools')
        self.target.install_packages(['open-vm-tools', 'open-vm-dkms'])