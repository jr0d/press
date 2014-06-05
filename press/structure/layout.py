from press.parted import PartedInterface
from press.udev import UDevHelper
from press.structure.size import Size


class Disk(object):
    size = 0

    def __init__(self, path, partition_table):
        """
        """
        self.path = path
        self.partition_table = partition_table


class PartitionTable(object):
    partitions = list()

    def __init__(self, table_type, size, partition_start=1048576, gap=1048576):
        """
        Calculates padding with all size operations
        """

        valid_types = ['gpt', 'msdos']
        if table_type not in valid_types:
            raise ValueError('table not supported: %s' % table_type)
        self.type = table_type
        self.size = Size(size)
        self.partition_start = Size(partition_start)
        self.gap = Size(gap)

    def _validate_partition(self, partition):
        if not isinstance(partition, Partition):
            return ValueError('Expected Partition instance')
        if self.partitions:
            if self.size < self.current_usage + partition.size + self.gap:
                raise LayoutValidationError(
                    'The partition is too big. %s > %s' % (self.current_usage, partition.size))
        elif self.size < partition.size + self.partition_start:
            raise LayoutValidationError(
                'The partition is too big. %s > %s' % (self.current_usage, partition.size))

        if partition.size < Size('1MiB'):
            raise LayoutValidationError('The partition cannot be < 1MiB.')

    @property
    def current_usage(self):
        if not self.partitions:
            return Size(0)

        used = Size(self.partition_start)
        for partition in self.partitions:
            used = used + partition.size + self.gap
        return used

    @property
    def free_space(self):
        if not self.partitions:
            return Size(self.partition_start)
        return self.size - self.current_usage - self.gap

    def add_partition(self, partition):
        self._validate_partition(partition)
        self.partitions.append(partition)

    def get_free_space_by_percentage(self, percent):
        return Size(self.free_space * (percent / 100.0))


class Partition(object):
    """
    A partition class, used to represent a partition logically. When this
    logical representation is writen to the disk, the parted_id class variable
    will be populated with the physical id. After creation, we will try to
    enumerate the /dev/link
    """

    parted_id = None
    device = None

    def __init__(self, type_or_name, size, boot=False,
                 lvm=False, swap=False, file_system=None, mount_point=None):
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
        self.swap = swap
        self.file_system = file_system
        self.mount_point = mount_point


class VolumeGroup(object):
    """
    Nearly a clone of the PartitionTable container, but for Logical Volumes. There
    are two many naming differences to subclass, however.

    """
    logical_volumes = list()

    def __init__(self, name, physical_volumes, pe_size=33554432):
        self.name = name
        self.physical_volumes = physical_volumes
        self.size = self.__calculate_size()
        self.pe_size = pe_size
        self.total_extents = self.size.bytes / pe_size

    def __calculate_size(self):
        size = Size(0)
        for pv in self.physical_volumes:
            size += pv.size
        return size

    @property
    def current_usage(self):
        used = Size(0)
        if not self.logical_volumes:
            return used
        for volume in self.logical_volumes:
            used += volume.size
        return used

    @property
    def current_pe(self):
        return self.current_usage.bytes / self.pe_size

    @property
    def free_space(self):
        return self.size - self.current_usage

    @property
    def free_pe(self):
        return self.free_space.bytes / self.pe_size

    def _validate_volume(self, volume):
        if not isinstance(volume, LogicalVolume):
            return ValueError('Expected LogicalVolume instance')
        if self.total_extents < self.current_pe + volume.size.bytes / self.pe_size:
            raise LayoutValidationError(
                'The volume is too big. %d PE > %d PE' % (volume.size.bytes / self.pe_size,
                                                          self.total_extents))

    def add_volume(self, volume):
        self._validate_volume(volume)
        self.logical_volumes.append(volume)

    def get_free_space_by_percentage(self, percent):
        return Size(self.free_space * (percent / 100.0))


class LogicalVolume(object):
    """
    Very similar to Partition, device is the /dev/link after the device is created.
    """
    device = None

    def __init__(self, name, size, swap=False, file_system=None, mount_point=None):
        self.name = name
        self.size = Size(size)
        self.swap = swap
        self.file_system = file_system
        self.mount_point = mount_point


class FileSystem(object):
    """
    Due the the heavy variance in options, in the future FileSystem should be a base class
    that is extended by individual fs_types, ie class EXT4, class XFS
    """
    def __init__(self, fs_type, size, fs_label=None, superuser_reserve=.03, stride_size=4096, stripe=65536):
        self.fs_type = fs_type
        self.fs_label = fs_label
        self.superuser_reserve = superuser_reserve
        self.block_size = stride_size
        self.stripe = stripe


class LayoutValidationError(Exception):
    pass


class PhysicalDiskException(Exception):
    pass


class Layout(object):
    """
    The highest level class.
    """
    disks = list()
    volume_groups = list()

    def __init__(self, subsystem='all',
                 use_fibre_channel=True, use_loop_devices=True,
                 parted_path='/sbin/parted',
                 default_partition_start=1048576, default_gap=1048576, default_alignment=4096,
                 disk_association='explicit',
                 *args, **kwargs):
        """
        Docs, maybe later

        disk_association: explicit: path must be associated with Disk object
                          first: Use only the first available disk, subsequent calls to add_disk
                            trigger an exception
                          any: The first available disk is used that can accommodate the
                            partition table
        """

        self.fc_enabled = use_fibre_channel
        self.loop_enabled = use_loop_devices
        self.parted_path = parted_path
        self.default_partition_start = default_partition_start
        self.default_gap = default_gap
        self.default_alignment = default_alignment
        self.disk_association = disk_association
        self.udev = UDevHelper()
        self.udisks = self.udev.discover_valid_storage_devices(self.fc_enabled, self.loop_enabled)
        if not self.udisks:
            raise PhysicalDiskException('There are no valid disks.')
        self.available_devices = [{
                                      'DEVNAME': udisk.get('DEVNAME'),
                                      'DEVLINKS': udisk.get('DEVLINKS'),
                                      'DEVPATH': udisk.get('DEVPATH')
                                  }
                                  for udisk in self.udisks]

    def _find_device_by_ref(self, ref):
        for idx in xrange(len(self.available_devices)):
            device  = self.available_devices[idx]
            if ref ==  device['DEVNAME']:
                return idx
            if ref == device.get('DEVPATH'):
                return idx
            for link in device.get('DEVLINKS'):
                if ref == link:
                    return idx
        return -1

    def _find_device_by_size(self, size):
        for idx in xrange(len(self.available_devices)):
            device = self.available_devices[idx]['DEVNAME']
            parted = PartedInterface(device, self.parted_path)
            if size < Size(parted.get_size()):
                return idx
        return -1

    def add_disk(self, disk):
        if not isinstance(disk, Disk):
            raise ValueError('Expected Disk instance.')
        if not self.available_devices:
            raise PhysicalDiskException('There are no more available devices.')
        if self.disk_association == 'explicit':
            if not disk.path:
                raise PhysicalDiskException('explicit lookup requires an explicit name.')
            idx = self._find_device_by_ref(disk.path)
            if idx == -1:
                raise PhysicalDiskException('%s is not present.' % disk.path)
            real_disk = self.available_devices.pop(idx)['DEVNAME']
        elif self.disk_association == 'first':
            real_disk = self.available_devices[0]
            self.available_devices = list()
        elif self.disk_association == 'any':
            idx = self._find_device_by_size(disk.partition_table.size)
            if idx == -1:
                raise PhysicalDiskException('No disk large enough for partition table.')
            real_disk = self.available_devices.pop(idx)
        else:
            raise ValueError('Unsupported association')

        parted = PartedInterface(real_disk)
        disk.size = Size(parted.get_size())
        if disk.size < disk.partition_table.size:
            raise PhysicalDiskException('Partition table is larger than target disk')

        self.disks.append(disk)

