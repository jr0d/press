
from press.chroot.base import Chroot

from press.cli import run
import logging


log = logging.getLogger(__name__)


class DebianChroot(Chroot):

    def __configure_boot_loader(self):
        """
        This will look for a 'grub' key in the config, and if present update the grub command line default.
        This assumes that the base image has the correct options (ie. not serial console), and we only override if
        values are set in the yaml config.

        """
        if self.config.get('grub'):
            log.info('Setting boot loader options from config')
            run("sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT.*/GRUB_CMDLINE_LINUX_DEFAULT=\"%s\"/g' /etc/default/grub" %
                self.config['grub']['options'], raise_exception=True)
        else:
            log.info('Boot loader options not set in config')

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
        self.__configure_boot_loader()
        # TODO figure how we can identify disk for bootloader.
        self.install_bootloader('/dev/sda')