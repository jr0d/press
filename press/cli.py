import logging
import shlex
import subprocess

log = logging.getLogger(__name__)


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
    """Runs a command and stores the important bits in an attribute string.

    :param command: Command to execute.
    :type command: str.

    :param bufsize: Buffer line size.
    :type bufsize: int.

    :param dry_run: Should we perform a dry run of the command.
    :type dry_run: bool.

    :returns: :func:`press.cli.AttributeString`.

    """
    log.debug('Running: %s' % command)
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

    log.debug('Return Code: %d' % ret)
    if out:
        log.debug('stdout: \n%s' % out.strip())
    if err:
        log.debug('stderr: \n%s' % err.strip())
    attr_string = _AttributeString(out)
    attr_string.stderr = err
    attr_string.returncode = ret
    attr_string.command = command
    return attr_string
