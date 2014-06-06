import shlex
import subprocess


class _AttributeString(str):
    def __init__(self, x):
        """
        For introspection
        """
        str.__init__(x)
        self.stderr = ''
        self.returncode = None
        self.command = ''
        self.comments = ''

    @property
    def stdout(self):
        return self


def run(command, bufsize=1048567, dry_run=False):
    """
    Runs a command and stores the important bits in an attribute string.
    :dry_run: For testing
    :return: _AttributeString
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
