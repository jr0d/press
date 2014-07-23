
from press.cli import run


class BasePost(object):
    """
    Base Post Class.
    """

    def userexist(self, username):
        """
        Check if a user exist.
        """
        ret = run('id %s' % username)
        if ret.returncode == 0:
            return True
        return False

    def useradd(self, username):
        """
        Creates a user with defaults options.

        :param username: The username to add.
        :returns: `press.cli._AttributeString`
        """

        ret = run('useradd %s' % username)
        return ret

    def passwd(self, username, password):
        """
        Set the password for a user.

        :param username: The username of account for password to be changed.
        :param password: The new password to set on account.
        :return: `press.cli._AttributeString`
        """
        if self.userexist(username):
            ret = run('echo %s | passwd %s --stdin' % (password, username))
            if ret.returncode == 0:
                return ret
