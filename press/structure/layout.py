from collections import OrderedDict
from press.parted import PartedInterface
from press.udev import UDevHelper
from .disk import Disk
from .size import Size

from .exceptions import PhysicalDiskException


class Layout(object):
    """
    The highest level class.
    """
    disks = list()
    volume_groups = list()

    def __init__(self, subsystem='all',
                 use_fibre_channel=True, use_loop_devices=True, loop_only=False,
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
        if loop_only:
            self.udisks = [udisk for udisk in self.udisks if 'loop' in udisk['DEVNAME']]

        if not self.udisks:
            raise PhysicalDiskException('There are no valid disks.')

        self.disks = OrderedDict()
        self.__populate_disks()

    def __populate_disks(self):
        for udisk in self.udisks:
            device = udisk.get('DEVNAME')
            parted = PartedInterface(device, self.parted_path)
            size = parted.get_size()
            disk = Disk(devname=device,
                        devlinks=udisk.get('DEVLINKS'),
                        devpath=udisk.get('DEVPATH'), size=size)
            self.disks[device] = disk

    def find_device_by_ref(self, ref):
        for disk in self.disks.values():
            if ref == disk.devname:
                return disk
            if ref == disk.devpath:
                return disk
            for link in disk.devlinks:
                if ref == link:
                    return disk

    def find_device_by_size(self, size):
        for disk in self.disks.values():
            if size < disk.size:
                return disk


    @property
    def allocated(self):
        l = list()
        for disk in self.disks.values():
            if disk.partition_table:
                l.append(disk)
        return l

    @property
    def unallocated(self):
        l = list()
        for disk in self.disks.values():
            if not disk.partition_table:
                l.append(disk)
        return l

    def add_partition_table_from_model(self, partition_table):
        unallocated = self.unallocated
        if not unallocated:
            raise PhysicalDiskException('There are more available disks')

        if partition_table.disk == 'first':
            disk = unallocated[0]

        elif partition_table.disk == 'any':
            disk = self.find_device_by_size(partition_table.allocated_space)
            if not disk:
                raise PhysicalDiskException('There is no suitable disk, table is too big')

        else:
            disk = self.find_device_by_ref(partition_table.disk)
            if not disk:
                raise PhysicalDiskException('Could not associate disk, %s was not found' %
                                            partition_table.disk)

        disk.new_partition_table(partition_table.type, partition_start=self.default_partition_start,
                                 gap=self.default_gap, alignment=self.default_alignment)

        for partition in partition_table.partitions:
            disk.partition_table.add_partition(partition)


