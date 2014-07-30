
from press.cli import run
import logging
import os


log = logging.getLogger(__name__)


class PostException(Exception):
    pass


class Post(object):
    """
    Base Post Class.
    """

    def __init__(self, newroot):
        """
        Starts post process.

        :param newroot: String path to our new root.
        """
        self.__bind_mount(prefix='/mnt/press',
                          mount_points=['/proc', '/dev', '/sys'])
        self.real_root = os.open('/', os.O_RDONLY)
        os.chroot(newroot)
        os.chdir('/')

    def __exit__(self):
        """
        Exits an active chroot
        """
        if self.real_root:
            os.fchdir(self.real_root)
            os.chroot('.')
            os.chdir('/')

    @staticmethod
    def __bind_mount(prefix, mount_points):
        """

        :param mount_points:
        :return:
        """
        for mount_point in mount_points:
            log.info('Bind mounting %s to %s%s' % (
                mount_point, prefix, mount_point))
            run('mount --rbind %s %s%s' % (mount_point, prefix, mount_point))

    def useradd(self, username):
        """
        Creates a user with defaults options.

        :param username: The username to add.
        :returns: `press.cli._AttributeString`
        """

        ret = run('useradd %s' % username)
        if not ret.returncode == 0:
            log.error('useradd failed with return_code: %s. Reasons: %s' % (
                ret.returncode, ret.stderr)
            )
            raise PostException(ret.stderr)
        return ret

    def passwd(self, username, password):
        """
        Set the password for a user.

        :param username: The username of account for password to be changed.
        :param password: The new password to set on account.
        :return: `press.cli._AttributeString`
        """
        ret = run('echo %s | passwd %s --stdin' % (password, username))
        if not ret.returncode == 0:
            log.error('passwd failed with return_code: %s. Reasons: %s' % (
                ret.returncode, ret.stderr)
            )
            raise PostException(ret.stderr)
        return ret

    def execute(self, script):
        """
        Executes a script using cli.

        :param script: A full path to script to run
        """
        ret = run('%s' % script)
        if not ret.returncode == 0:
            log.error('failed to execute %s, return_code: %s. Reasons: %s' % (
                script, ret.returncode, ret.stderr)
            )
            raise PostException(ret.stderr)
        return ret

    def grub_install(self, disk):
        """
        Install grub on disk.

        :param disk: Disk as a string /dev/sda
        """
        return NotImplemented

    def install_packages(self, packages=[]):
        """
        Install packages using the system's Package Manager.

        :param packages: A list of strings. Each string is a debian package
        to be installed.
        """
        return NotImplemented
