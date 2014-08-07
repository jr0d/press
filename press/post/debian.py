
from press.post.base import Post

from press.cli import run
import logging


log = logging.getLogger(__name__)


class DebianPost(Post):

    def apt_get_install(self, packages):
        """
        Install a package using apt.
        :param packages: A list of strings. Each string is a debian package
        to be installed.
        """
        log.debug('Installing %s with apt-get' % packages)
        return run('apt-get -y install %s' % ' '.join(packages),
                   raise_exception=True)

    def install_packages(self, packages):
        """
        Install packages using the system's Package Manager.

        :param packages: A list of strings. Each string is a debian package
        to be installed.
        """
        return self.apt_get_install(packages)

    def grub_install(self, disk):
        """
        Install grub on disk.

        :param disk: Disk as a string /dev/sda
        """
        log.debug('Setting up grub on %s' % disk)
        debconf = 'grub-pc grub-pc/install_devices multiselect %s' % disk
        run('echo "%s" | debconf-set-selections' % debconf,
            raise_exception=True)
        run('grub-mkconfig -o /boot/grub/grub.cfg', raise_exception=True)
        run('grub-install %s' % disk, raise_exception=True)