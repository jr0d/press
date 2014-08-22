
from press.chroot.base import Chroot

from press.cli import run
import logging


log = logging.getLogger(__name__)


class DebianChroot(Chroot):

    def install_bootloader(self, disk):
        """
        Install bootloader on disk.

        :param disk: Disk as a string /dev/sda
        """
        log.debug('Setting up GRUB on %s' % disk)
        debconf = 'grub-pc grub-pc/install_devices multiselect %s' % disk
        run('echo "%s" | debconf-set-selections' % debconf,
            raise_exception=True)
        run('grub-mkconfig -o /boot/grub/grub.cfg', raise_exception=True)
        run('grub-install %s' % disk, raise_exception=True)

    def apply(self):
        """
        Run entire Chroot process.
        """
        self.add_users()
        # TODO figure how we can identify disk for bootloader.
        self.install_bootloader('/dev/sda')