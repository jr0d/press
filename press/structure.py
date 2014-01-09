from decimal import Decimal, InvalidOperation

class Partition(object):
    """

    Represents the base container.

    __device__ is set when the partition object is linked to a pysical disk.

    __file_system__ a FileSystem object when a file system is assigned

    __vg_parent__ is only set when the partition is marked as a pysical
    volume and is part of a volume group. VGroup object.

    __pv__ bool, is the partition is initialized as, or intended to be, a
    pysical volume.

    """


    def __init__(self, name='', fs_type=None, size=0, mount_point=None):
        self.__device__ = None
        self.__file_system__ = None
        self.__vg_parent__ = None
        self.__pv__ = False

        self.name = name
        self.fs_type = fs_type
        if self.fs_type:
            self.__file_system__ = FileSystem(self.fs_type)
        self.size = Size(size)
        self.mount_point = mount_point

    def __repr__(self):
        return '%s : %s %s' % (Partition.__mro__[0], self.fs_type,
                self.size.humanize)

    def __str__(self):
        return '%s [ %s, %s ]' % (self.name, self.fs_type, self.size.humanize)


class FileSystem(object):
    def __init__(self, fs_type='ext4'):
        self.fs_type = fs_type


class VGroup(object):
    def __init__(self, name, partitions=list()):
        self.name = name
        self.partitions = partitions


class LVolume(object):
    def __init__(
            self, name='', fs_type=None, size=0, mount_point=None):
        self.name = name,
        self.fs_type = fs_type
        if self.fs_type:
            fs_type = FileSystem(fs_type)
        self.size = Size(size)
        self.mount_point = mount_point

    def __repr__(self):
        return '%s : %s %s' % (LVolume.__mro__[0], self.fs_type,
            self.size.humanize)


class Layout(object):
    __on_disk__ = False

    def __init__(self, disk_size, table='gpt'):
        self.disk_size = Size(disk_size)
        self.table = table
        self.partitions = list()
        self.vgroups = list()

    def add_partition(self, partition):
        try:
            self._validate_partition(partition)
        except AttributeError as ae:
            raise LayoutValidationError('The partition object was invalid.' + \
                    '\n[%s]' % str(ae))

        self.partitions.append(partition)

    def remove_partition(self, index=None):
        if not index:
            raise LayoutValidationError('You must specify an index')
        self.partitions.pop(index)

    def get_partition_index_by_name(self):
        pass

    def show(self):
        for partition in self.partitions:
            print partition

    def get_used_size(self):
        if not len(self.partitions):
            return Size(0)

        used = Size(0)
        for partition in self.partitions:
            used = used + partition.size
        return used

    def add_partition_percent(self, name, fs_type, percent):
        """
        Creates a partition using a percentage of available disk space.
        """
        current_size = self.get_used_size()
        available = self.disk_size - current_size
        size = Size(available.bytes * (percent/100.0))
        self.add_partition(Partition(name, fs_type, size.bytes))

    def add_partition_fill(self, name, fs_type):
        current_size = self.get_used_size()
        partition_size = self.disk_size - current_size
        self.add_partition(Partition(name, fs_type, partition_size.bytes))

    def add_partition_exact(self, name, fs_type, size):
        self.add_partition(Partition(name, fs_type, size))

    def _validate_partition(self, partition):
        ## check if there is available space
        if len(self.partitions):
            if self.disk_size < self.get_used_size() + partition.size:
                raise LayoutValidationError('The partition is too big.')
        else:
            if self.disk_size < partition.size:
                raise LayoutValidationError('The partition is too big.')

        if partition.size < Size('1MiB'):
            raise LayoutValidationError('The partition cannot be < 1MiB.')

    def _enum_partitions(self):
        return enumerate([partition.name for partition in self.partitions])

    def __repr__(self):
        return '<%s>  : %d [%s]' % (
                self.__class__.__name__,
                self.disk_size.bytes,
                self.table
                )

    def __str__(self):
        """

        """
        output = 'Partition Table (%s):\n' % (self.table) + \
                 'Disk Size: %d (%s)\n' % (
                         self.disk_size.bytes, self.disk_size)

        for partition in self.partitions:
            output += '[%s]\t%s\t%s\n' % (partition.name, partition.fs_type,
                                          partition.size)

        output += '\t\t\tremaining: %s / %s' % (self.get_used_size(),
                                                self.disk_size)
        return output


class Size(object):
    byte = 1
    kibibyte = 1024
    mebibyte = kibibyte**2
    gibibyte = kibibyte**3
    tebibyte = kibibyte**4
    pebibyte = kibibyte**5
    exbibyte = kibibyte**6
    zebibyte = kibibyte**7
    yobibyte = kibibyte**8

    # Because we are dealing with disks, we'll probably need decimal byte notation

    kilobyte = 1000
    megabyte = kilobyte**2
    gigabyte = kilobyte**3
    terabyte = kilobyte**4
    petabyte = kilobyte**5
    exabyte = kilobyte**6
    zettabyte = kilobyte**7
    yottabyte = kilobyte**8

    sector = 512

    symbols = {
        'b': byte,
        'k': kilobyte,
        'kB': kilobyte,
        'KiB': kibibyte,
        'M': megabyte,
        'MB': megabyte,
        'MiB': mebibyte,
        'G': gigabyte,
        'GB': gigabyte,
        'GiB': gibibyte,
        'T': terabyte,
        'TB': terabyte,
        'TiB': tebibyte,
        'PB': petabyte,
        'PiB': pebibyte,
        'EB': exabyte,
        'EiB': exbibyte,
        'YB': yottabyte,
        'YiB': yobibyte,
        's': sector
    }

    def __init__(self, value):
        self.bytes = self._convert(value)

    def _convert(self, value):
        if isinstance(value, (int, long)):
            if value > self.yobibyte:
                raise SizeObjectValError('Value is impossibly large.')
            return value

        if isinstance(value, (float, Decimal)):
            return int(round(value))

        if not isinstance(value, (str, unicode)):
            raise SizeObjectValError(
                'Value is not in a format I can understand')

        if value.isdigit():
            return int(value)

        valid_suffices = self.symbols.keys()
        suffix_index = 0
        for valid_suffix in valid_suffices:
            our_index = value.find(valid_suffix)
            if our_index and our_index != -1:
                suffix_index = our_index
                break
        if not suffix_index:
            raise SizeObjectValError(
                'Value is not in a format I can understand. Invalid Suffix.')

        val, suffix = value[:suffix_index].strip(), value[suffix_index:].strip()

        if suffix not in valid_suffices:
            raise SizeObjectValError(
                'Value is not in a format I can understand. Invalid Suffix.')

        try:
            val = Decimal(val)
        except InvalidOperation:
            raise SizeObjectValError(
                'Value is not in a format I can understand. '
                'Could not convert value to int')

        return int(round(val * self.symbols[suffix]))

    @property
    def humanize(self):
        units = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'TiB']
        if self.bytes < self.symbols['KiB']:
            return '%d b' % self.bytes

        for idx in range(1, len(units)):
            if self.bytes < self.symbols[units[idx]]:
                unit = units[idx-1]
                return '%s %s' % (Decimal(self.bytes) / self.symbols[unit], unit)

        raise SizeObjectValError('Something very strange has happened.')

    @property
    def megabytes(self):
        return Decimal(self.bytes) / self.megabyte

    def __repr__(self):
        rep = '<%s> : %ib' % (self.__class__.__name__, self.bytes)
        return rep

    def __str__(self):
        return self.humanize

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
