import os
import logging
import shlex
import subprocess

log = logging.getLogger(__name__)


class AttributeString(str):
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


class CLIException(Exception):
    """
    Exception used by cli.run function
    """
    pass


def run(command, bufsize=1048567, dry_run=False, raise_exception=False, ignore_error=False,
        quiet=False, env=None):
    """Runs a command and stores the important bits in an attribute string.

    :param command: Command to execute.
    :type command: str.

    :param bufsize: Buffer line size.
    :type bufsize: int.

    :param dry_run: Should we perform a dry run of the command.
    :type dry_run: bool.

    :returns: :func:`press.cli.AttributeString`.

    """
    if not quiet:
        log.debug('Running: %s' % command)
    our_env = os.environ.copy()
    our_env.update(env or dict())
    cmd = shlex.split(str(command))
    if not dry_run:
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             bufsize=bufsize,
                             env=our_env)
        out, err = p.communicate()
        ret = p.returncode
    else:
        out, err, ret = '', '', 0

    if not quiet:
        log.debug('Return Code: %d' % ret)
        if out:
            log.debug('stdout: \n%s' % out.strip())
    if ret and not ignore_error:
        log.error('Return: %d running: %s stdout: %s\nstderr: \n%s' % (ret,
                                                                       command,
                                                                       out.strip(),
                                                                       err.strip()))
        if raise_exception:
            raise CLIException(err)

    attr_string = AttributeString(out)
    attr_string.stderr = err
    attr_string.returncode = ret
    attr_string.command = command
    return attr_string


def find_in_path(filename):
    if os.path.isabs(filename):
        if os.path.exists(filename):
            return filename
        else:
            return None

    for path in os.environ['PATH'].split(os.pathsep):
        abspath = os.path.join(path, filename)
        if os.path.exists(abspath):
            return abspath


