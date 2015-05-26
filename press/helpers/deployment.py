import cli
import logging
import os
import shutil

from tempfile import mkstemp

log = logging.getLogger(__name__)


def recursive_makedir(path, mode=0775):
    if os.path.isdir(path):
        return False

    if os.path.exists(path):
        raise IOError('%s exists but is NOT a directory' % path)

    os.makedirs(path, mode)
    return True


def recursive_remove(path):
    if not os.path.exists(path):
        log.debug('Path, %s, does not exist, nothing to do' % path)
        return

    if os.path.islink(path):
        log.debug('Removing symbolic link at: %s' % path)
        os.unlink(path)
        return

    log.debug('Removing directory: %s' % path)
    shutil.rmtree(path)


def read(filename, splitlines=False):
    """
    Reads a file by absolute path and returns it's content.

    :param filename: Absolute path to a file.
    :type filename: str.

    :return: str.

    """
    with open(filename, 'r') as f:
        read_data = f.read()
    if splitlines:
        return read_data.splitlines()
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


def replace_line_matching(data, match, newline):
    lines = data.splitlines()
    for idx in xrange(len(lines)):
        if match in lines[idx]:
            lines[idx] = newline
    return '\n'.join(lines)


def create_symlink(src, link_name, remove_existing_link=False):
    if os.path.exists(link_name):
        if os.path.islink(link_name):
            if remove_existing_link:
                os.unlink(link_name)
                log.warning('Removing existing link')
            else:
                log.warning('symbolic link %s already exists' % link_name)
                return
        log.error('File already exists at target: %s' % link_name)
        return

    os.symlink(src, link_name)


def remove_file(path):
    if not os.path.exists(path):
        return
    if os.path.isdir(path):
        log.error('Path is a directory, use recursive_remove')
        return

    os.unlink(path)


def tar_extract(archive_path, chdir=''):
    bzip_extensions = ('bz2', 'tbz', 'tbz2')
    compress_method = 'z'
    use_bzip = bool([i for i in bzip_extensions if archive_path.endswith(i)])
    if use_bzip:
        compress_method = 'j'

    return cli.run('tar -%sxf %s%s' % (compress_method, archive_path,
                                       chdir and ' -C %s' % chdir or ''))