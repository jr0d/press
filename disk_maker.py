
class Partition(object):
    '''Represents the base container.'''
    __device__ = None
    __file_system__ = None
    def __init__(self, name='', fs_type=None, size=0):
        self.name = name
        self.fs_type = fs_type
        self.size = Size(size)
    
    def __repr__(self):
        return '%s : %s %s' % (Partition.__mro__[0], self.fs_type, 
                self.size.humanize())
    def __str__(self):
        return '%s [ %s, %s ]' % (self.name, self.fs_type, self.size.humanize())


class FileSystem(object):
    def __init__():
        pass

class LVMGroup(object):
    pass

class Layout(object):
    def __init__(self, disk_size, table='gpt'):
        self.disk_size = Size(disk_size)
        self.table = table
        self.partitions = list()

    def add_partition(self, partition):
        try:
            self._validate_partition(partition)
        except AttributeError:
            raise LayoutValidationError('The partition object was invalid.')

        self.partitions.append(partition)

    def remove_partition(self, index=None):
        if not index:
            raise LayoutValidationError('You must specify an index')
        self.partitions.pop(index)

    def get_partition_index_by_name():
        pass

    def show(self):
        for partition in partitions:
            print partition
    
    def get_used_size(self):
        if not len(self.partitions):
            return Size(0)

        used = Size(0)
        for partition in self.partitions:
            used = used + partition.size
        return used

    def add_partition_percent(self, name, percent, fs_type):
        pass

    def add_partition_fill(self, name, fs_type):
        pass

    def _validate_partition(self, partition):
        ## check if there is available space
        if len(self.partitions):
            if self.disk_size < self.get_used_size() + partition.size:
                raise LayoutValidationError('The partition is too big.')
        else:
            if self.disk_size < partition.size:
                raise LayoutValidationError('The partition is too big.')

    def _enum_partitions(self):
        return enumerate([partition.name for partition in self.partitions])

    def __repr__(self):
        return Layout.__mro__[0]

    def __str__(self):
        output = 'Partition Table (%s):\n' % (self.table) + \
                 'Disk Size: %d (%s)\n' % (
                         self.disk_size.bytes, self.disk_size)

        for partition in self.partitions:
            output = output + \
            '[%s]\t%s\t%s\n' % (partition.name, partition.fs_type,
                    partition.size)

        output = output + '\t\t\tremaining: %s / %s' % (self.get_used_size(),
                self.disk_size)

        return output

class Size(object):
    byte = 2**3
    kilobyte = 2**10
    megabyte = 2**20
    gigabyte = 2**30
    terabyte = 2**40
    
    def __init__(self, value):
        self.bytes = self._convert(value) 
        

    def _convert(self, value):
        valid_suffix = ['k', 'M', 'G', 'T']
        if type(value) == int:
            return value

        if value.isdigit():
            return int(value)

        if type(value) != str:
            raise SizeObjectValError(
                'Value is not in a format I can understand')

        val, suffix = (value[:-1], value[-1])

        if suffix not in valid_suffix:
            raise SizeObjectValError(
            'Value is not in a format I can understand. Invalid Suffix.')

        try:
            val = int(val)
        except ValueError:
            raise SizeObjectValError(
                'Value is not in a format I can understand. ' + \
                'Could not convert value to int')
        if suffix == 'k':
            return val * self.kilobyte

        if suffix == 'M':
            return val * self.megabyte

        if suffix == 'G':
            return val * self.gigabyte

        if suffix == 'T':
            return val * self.terabyte

        raise SizeObjectValError(
                'Value is not in a format I can understand')
        
    def _units(self):
        return [('T', self.terabyte),
               ('G', self.gigabyte),
               ('M', self.megabyte),
               ('k', self.kilobyte),
               ('b', self.byte)]

    def humanize(self):
        human = None
        for unit in self._units():
            if self.bytes >= unit[1]:
                human = str(self.bytes / unit[1]) + unit[0]
                break
        return human

    def megabytes(self):
        return self.bytes / self.megabyte
                
    def __repr__(self):
        rep = '%s : %ib' % (Size.__mro__[0], self.bytes)
        return rep

    def __str__(self):
        return self.humanize()

    def __add__(self, other):
        return Size(self.bytes + other.bytes)

    def __sub__(self, other):
        return Size(self.bytes - other.bytes)

    def __mul__(self, other):
        return Size(self.bytes * other.bytes)

    def __div__(self, other):
        'dont devide by zero.'
        return Size(other.bytes/self.bytes)
    
    def __lt__(self, other):
        return self.bytes < other.bytes

    def __le__(self, other):
        return self.bytes <= other.bytes

    def __eq__(self, other):
        return self.bytes == other.bytes

    def __ne__(self, other):
        return self.bytes <> other.bytes

    def __gt__(self, other):
        return self.bytes > other.bytes

    def __ge__(self, other):
        return self.bytes >= other.bytes

    def __truedev__(self, other):
        'dont device by zero'
        return Size(other.bytes/self.bytes)

class PartitionError(Exception):pass
class SizeObjectValError(Exception):pass
class LayoutValidationError(Exception):pass
