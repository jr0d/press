
import os


def read(filename):
    """
    Reads a file by absolute path and returns it's content.

    :param filename: Absolute path to a file.
    :type filename: str.

    :return: str.

    """
    with open(filename, 'r') as f:
        read_data = f.read()
    f.close()
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