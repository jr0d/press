import shlex
import subprocess


class _AttributeString(str):
    def __init__(self, x):
        """Class that inherits from str and provides additional attributes
        for storing subprocess command execution.
        """
        str.__init__(x)
        self._stderr = ''
        self._command = ''
        self._comments = ''
        self._returncode = None

    @property
    def stdout(self):
        """Returns the command standard output.
        """
        return self

    @property
    def stderr(self):
        """Returns the stderr attribute.
        """
        return self._stderr

    @stderr.setter
    def stderr(self, value):
        self._stderr = value

    @property
    def command(self):
        """Returns the command attribute.
        """
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def comments(self):
        """Returns the comments attribute.
        """
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value

    @property
    def returncode(self):
        """Returns the returncode attribute.
        """
        return self._returncode

    @returncode.setter
    def returncode(self, value):
        self._returncode = value


def run(command, bufsize=1048567, dry_run=False):
    """Runs a command and stores the important bits in an attribute string.

    :param command: Command to execute.
    :type command: str.

    :param bufsize: Buffer line size.
    :type bufsize: int.

    :param dry_run: Should we perform a dry run of the command.
    :type dry_run: bool.

    :returns: :func:`press.cli._AttributeString`.

    """

    cmd = shlex.split(str(command))
    if not dry_run:
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             bufsize=bufsize)
        out, err = p.communicate()
        ret = p.returncode
    else:
        out, err, ret = '', '', 0

    attr_string = _AttributeString(out)
    attr_string.stderr = err
    attr_string.returncode = ret
    attr_string.command = command
    return attr_string
