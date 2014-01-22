from press.parted import PartedInterface
from press.structure.size import Size


class Disk(object):
    def __init__(self, path, partition_table):
        """
        """
        self.path = path
        self.partition_table = partition_table


class PartitionTable(object):
    partitions = list()

    def __init__(self, table_type, size, partition_start=1048576, gap=1048576):
        valid_types = ['gpt', 'msdos']
        if table_type not in valid_types:
            raise ValueError('table not supported: %s' % table_type)
        self.type = table_type


class Partition(object):
    """
    A partition class, used to represent a partition logically. When this
    logical representation is writen to the disk, the parted_id class variable
    will be populated with the physical id. After creation, we will try to
    enumerate the /dev/link
    """

    parted_id = None
    device = None
    file_system = None

    def __init__(self, type_or_name, size, boot=False,
                 lvm=False, swap=False):
        """
        Constructor:

        size: a Size compatible value (see Size object documentation)..
        boot: set the boot flag on this partition when it is writen to disk
        lvm: set the lvm flag on this partition when it is written to disk
        name: the name of the partition, valid only on gpt partition tables
        """
        self.size = Size(size)
        self.boot = boot
        self.lvm = lvm
        self.name = type_or_name


class Layout(object):
    def __init__(self, disks):
        pass

