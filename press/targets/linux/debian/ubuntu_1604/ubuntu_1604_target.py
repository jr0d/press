import logging

from press.helpers import deployment, sysfs_info
from press.targets import GeneralPostTargetError
from press.targets.linux.grub2_debian_target import Grub2Debian
from press.targets.linux.debian.debian_target import DebianTarget

log = logging.getLogger(__name__)


class Ubuntu1604Target(DebianTarget, Grub2Debian):
    name = 'ubuntu_1604'
    dist = 'xenial'

    def check_for_grub(self):
        if sysfs_info.has_efi():
            _required_packages = ['shim-signed', 'grub-efi-amd64-signed']
            if self.install_packages(_required_packages):
                raise GeneralPostTargetError('Error installing required packages for grub2')

    def run(self):
        super(Ubuntu1604Target, self).run()
        self.grub_disable_recovery()
        self.check_for_grub()
        self.install_grub2()
