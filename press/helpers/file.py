import logging
import os
import shutil

from tempfile import mkstemp

log = logging.getLogger(__name__)


def read(filename):
    """
    Reads a file by absolute path and returns it's content.

    :param filename: Absolute path to a file.
    :type filename: str.

    :return: str.

    """
    with open(filename, 'r') as f:
        read_data = f.read()
    return read_data


def write(filename, data, append=False, mode=0644):
    """
    Writes to a file by absolute path.

    :param filename: Absolute path to a file.
    :type filename: str.

    :param data: A string of data which will be written to file.
    :type data: str.

    :param append: Should the file be appended to, or over-written.
    :type append: bool.

    :param mode: The linux permission mode to use for the file.
    :type mode: int.

    :return: None

    """

    # Use our append keyword argument to
    # determine our write mode.
    if append:
        write_mode = 'a'
    else:
        write_mode = 'w'

    with open(filename, write_mode) as f:
        f.write(data)

    # Last step lets change the file mode to specified mode
    os.chmod(filename, mode)


def replace_file(path, data):
    """
    Replace a file with data. Mode is maintained, ownership is not
    :param path:
    :param data:
    :return:
    """
    log.info('Replacing %s' % path)
    if not os.path.exists(path):
        log.warn('The file you want to replace does not exist, writing a new file')
        return write(path, data)
    if os.path.isdir(path):
        raise IOError('Cannot overwrite a directory')
    if not os.access(path, os.W_OK):
        raise IOError('Cannot write to target path')

    fp, temp_path = mkstemp()
    os.write(fp, data)
    os.close(fp)
    shutil.copymode(path, temp_path)
    # Cannot rely on os.rename, doing this manually
    os.unlink(path)
    shutil.copy(temp_path, path)
    os.unlink(temp_path)
