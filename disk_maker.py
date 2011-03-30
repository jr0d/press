
class Partition(object):
    '''Represents the base container.'''
    __device__ = None
    __file_system__ = None
    def __init__(self, fs_type=None, size=0):
        self.fs_type = fs_type
        self.size = Size(size)
    
    def __repr__(self):
        return '%s : %s %s' % (Partition.__mro__[0], self.fs_type, 
                self.size.humanize())

class FileSystem(object):
    def __init__():
        pass

class LVMGroup(object):
    pass

class Layout(object):
    def __init__(self, disk_size, table='gpt'):
        self.size = size
        self.partitions = list()

    def add_partition(self, partition):

        self.partitions.append(partition)

    def remove_partition(self, partition):
        pass

    def show(self):
        for partition in partitions:
            print partition


    def __repr__(self):
        pass

    def __str__(self):
        return self.__repr__()

    
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

        if type(value) != str:
            raise SizeObjectValError(
                'Value is not in a format I can understand')

        val, suffix = (value[:-1], value[-1])

        if suffix not in valid_suffix:
            raise SizeObjectValError(
                'Value is not in a format I can understand')

        try:
            val = int(val)
        except ValueError:
            raise SizeObjectValError(
                'Value is not in a format I can understand')

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
        return self.bytes + other.bytes

    def __sub__(self, other):
        return self.bytes - other.bytes

    def __mul__(self, other):
        return self.bytes * other.bytes

    def __div__(self, other):
        'dont devide by zero.'
        return other.bytes/self.bytes

    def __truedev__(self, other):
        'dont device by zero'
        return other.bytes/self.bytes

class PartitionError(Exception):pass
class SizeObjectValError(Exception):pass
