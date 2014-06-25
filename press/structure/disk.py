from .size import Size, PercentString
from .exceptions import PartitionValidationError


class Disk(object):
    def __init__(self, devname=None, devlinks=None, devpath=None, partition_table=None, size=0):
        """
        """
        self.devname = devname
        self.devlinks = devlinks or list()
        self.devpath = devpath
        self.size = Size(size)
        self.partition_table = partition_table

    def new_partition_table(self, table_type, partition_start=1048576, gap=1048576, alignment=4096):
        """Instantiate and link a PartitionTable object to Disk instance
        """
        self.partition_table = PartitionTable(table_type,
                                              self.size.bytes,
                                              partition_start=partition_start,
                                              gap=gap, alignment=alignment)


class PartitionTable(object):
    def __init__(self, table_type, size, partition_start=1048576, gap=1048576, alignment=4096):
        """Logical representation of a partition
        """

        valid_types = ['gpt', 'msdos']
        if table_type not in valid_types:
            raise ValueError('table not supported: %s' % table_type)
        self.type = table_type
        # size must be related to
        self.size = Size(size)
        self.partition_start = Size(partition_start)
        self.gap = Size(gap)
        self.alignment = Size(alignment)

        # This variable is used to store a pointer to the end of the partition
        # structure + (alignment - ( end % alignment ) )
        self.partition_end = Size(partition_start)
        self.partitions = list()

    def _validate_partition(self, partition):
        if not isinstance(partition, Partition):
            return ValueError('Expected Partition instance')
        if self.partitions:
            if self.size < self.current_usage + self.gap + partition.size:
                raise PartitionValidationError(
                    'The partition is too big. %s < %s' % (self.size - self.current_usage, partition.size))
        elif self.size < partition.size + self.partition_start:
            raise PartitionValidationError(
                'The partition is too big. %s < %s' % (self.size - self.current_usage, partition.size))

        if partition.size < Size('1MiB'):
            raise PartitionValidationError('The partition cannot be < 1MiB.')

    def calculate_total_size(self, size):
        """Calculates total size after alignment.
        """
        if isinstance(size, PercentString):
            if size.free:
                size = self.get_percentage_of_free_space(size.value)
            else:
                size = self.get_percentage_of_usable_space(size.value)
        return size + (self.alignment - size % self.alignment)

    @property
    def current_usage(self):
        return self.partition_end

    @property
    def free_space(self):
        if not self.partitions:
            return self.size - self.partition_start
        return self.size - (self.partition_end + self.gap)

    @property
    def physical_volumes(self):
        return [partition for partition in self.partitions if partition.lvm]

    def add_partition(self, partition):
        if partition.percent_string:
            adjusted_size = self.calculate_total_size(partition.percent_string)
        else:
            adjusted_size = self.calculate_total_size(partition.size)
        partition.size = adjusted_size
        self._validate_partition(partition)
        self.partitions.append(partition)
        self.partition_end += adjusted_size
        # update partition size

    def get_percentage_of_free_space(self, percent):
        return Size(self.free_space.bytes * percent)

    def get_percentage_of_usable_space(self, percent):
        return Size((self.size - self.partition_start).bytes * percent)

    def __repr__(self):
        out = 'Table: %s (%s / %s)\n' % (self.type, self.current_usage, self.size)
        for idx, partition in enumerate(self.partitions):
            out += '%d: %s %s\n' % (idx, partition.name, partition.size)
        return out


class Partition(object):
    """
    A partition class, used to represent a partition logically. When this
    logical representation is writen to the disk, the parted_id class variable
    will be populated with the physical id. After creation, we will try to
    enumerate the /dev/link
    """

    def __init__(self, type_or_name, size_or_percent, boot=False,
                 lvm=False, swap=False, file_system=None, mount_point=None):
        """
        Constructor:

        size: a Size compatible value (see Size object documentation)..
        boot: set the boot flag on this partition when it is writen to disk
        lvm: set the lvm flag on this partition when it is written to disk
             Layout will consider this a physical volume
        name: the name of the partition, valid only on gpt partition tables
        """
        if isinstance(size_or_percent, PercentString):
            self.size = Size(0)
            self.percent_string = size_or_percent
        else:
            self.size = Size(size_or_percent)
            self.percent_string = None

        self.boot = boot
        self.lvm = lvm
        self.name = type_or_name
        self.swap = swap
        self.file_system = file_system
        self.mount_point = mount_point

        self.partition_id = None
        self.devname = None