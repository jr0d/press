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
        bootloader_config = self.config.get('bootloader')
        if not bootloader_config:
            log.warning('Bootloader configuration is missing')
            return

        disk = self.config['bootloader'].get('target', 'first')
        if disk == 'first':
            self.install_bootloader(self.disks.keys()[0])
        else:
            self.install_bootloader(disk)