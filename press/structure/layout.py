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

        self.disks = self.__populate_disks()
        self.available_devices = self.disks.items()

    def __populate_disks(self):
        disks = dict()
        for udisk in self.udisks:
            device = udisk.get('DEVNAME')
            parted = PartedInterface(device, self.parted_path)
            size = parted.get_size()
            disk = Disk(devname=device,
                        devlinks=udisk.get('DEVLINKS'),
                        devpath=udisk.get('DEVPATH'), size=size)
            disks[disk.devname] = disk
        return disks

    def find_device_by_ref(self, ref):
        for idx in xrange(len(self.available_devices)):
            disk = self.available_devices[idx]
            if ref == disk.devname:
                return idx
            if ref == disk.devpath:
                return idx
            for link in disk.devlinks:
                if ref == link:
                    return idx
        return -1

    def find_device_by_size(self, size):
        for idx in xrange(len(self.available_devices)):
            disk = self.available_devices[idx]
            if size < disk.size:
                return idx
        return -1

    def add_partition_table_from_model(self, partition_table):
        if not self.available_devices:
            raise PhysicalDiskException('There are more available disks')

        if partition_table.disk == 'first':
            disk = self.available_devices.pop(0)

        elif partition_table.disk == 'any':
            idx = self.find_device_by_size(partition_table.allocated_space)
            if idx == -1:
                raise PhysicalDiskException('There is no suitable disk, table is too big')
            disk = self.available_devices.pop(idx)

        else:
            idx = self.find_device_by_ref(partition_table.disk)
            if idx == -1:
                raise PhysicalDiskException('Could not associate disk, %s was not found' %
                                            partition_table.disk)
            disk = self.available_devices.pop(idx)

        disk.new_partition_table(partition_table.type, partition_start=self.default_partition_start,
                                 gap=self.default_gap, alignment=self.default_alignment)
        for partition in partition_table.partitions:
            disk.partition_table.add_partition(partition)


