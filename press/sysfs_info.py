"""sysfs helpers
"""
import os


class SYSFSInfoException(Exception):
    pass


def parse_cookie(path):
    with open(path) as cookie_file:
        return cookie_file.read().strip()


def append_sys(path):
    os.path.join('/sys', path.lstrip('/'))


class AlignmentInfo(object):
    def __init__(self, devpath):
        self.attributes = {
            'alignment_offset': (None, 'alignment_offset'),
            'physical_block_size': (None, 'queue/physical_block_size'),
            'logical_block_size': (None, 'queue/physical_block_size'),
            'optimal_io_size': (None, 'queue/optimal_io_size')
        }
        self.devpath = devpath

    def __magic_set_attr(self, attr):
        val, path = self.attributes[attr]
        if val is not None:
            return val
        val = parse_cookie(os.path.join(self.devpath, path))
        if val.isdigit():
            val = int(val)
        self.attributes[attr] = (val, path)
        return val

    @property
    def alignment_offset(self):
        return self.__magic_set_attr('alignment_offset')

    @property
    def physical_block_size(self):
        return self.__magic_set_attr('physical_block_size')

    @property
    def logical_block_size(self):
        return self.__magic_set_attr('logical_block_size')

    @property
    def optimal_io_size(self):
        return self.__magic_set_attr('optimal_io_size')
