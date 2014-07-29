
from press.post.base import Post, PostException

from press.cli import run
import logging


log = logging.getLogger(__name__)


class DebianPost(Post):

    def apt_get_install(self, packages=[]):
        """
        Install a package using apt.
        :param packages: A list of strings. Each string is a debian package
        to be installed.
        """
        if packages:
            ret = run('apt-get -y install %s' % ' '.join(packages))
            if not ret.returncode == 0:
                log.error(
                    'apt_get_install failed with return_code: %s. Reasons: %s'
                    % ret.returncode, ret.stderr
                )
                raise PostException(ret.stderr)
            return ret

    def install_packages(self, packages=[]):
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
        run('grub-mkconfig -o /boot/grub/grub.cfg')
        run('grub-install %s' % disk)