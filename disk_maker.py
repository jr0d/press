
class Partition(object):
    '''Represents the base container.'''
    __device__ = None
    __file_system__ = None
    def __init__(self, fs_type=None, size=0):
        self._check_args(fs_type, size)
        self.fs_type = fs_type
        self.size = size

class FileSystem(object):
    __init__()

class LVMGroup(object, partition=None):
    pass

class Layout(object):
    def __init__(self, table='gpt'):
        self.table = table
        self.partitions = list()

    def add_partition(self, partition):
        


class PartitionError(Exception):pass

