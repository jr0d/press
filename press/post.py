
from press.cli import run
import logging


log = logging.getLogger(__name__)


class PostException(Exception):
    pass


class Post(object):
    """
    Base Post Class.
    """

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

    def grub_install(self, disk):
        """
        Install grub on disk.

        :param disk: Disk as a string /dev/sda
        """
        return NotImplemented
