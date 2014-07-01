import logging
import time
from collections import OrderedDict
from press.parted import PartedInterface, NullDiskException
from press.udev import UDevHelper
from .disk import Disk

from .exceptions import PhysicalDiskException, LayoutValidationError

log = logging.getLogger(__name__)


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
        self.udisks = self.udev.discover_valid_storage_devices(self.fc_enabled,
                                                               self.loop_enabled)
        if loop_only:
            self.udisks = [udisk for udisk in self.udisks if 'loop' in udisk['DEVNAME']]

        if not self.udisks:
            raise PhysicalDiskException('There are no valid disks.')

        self.disks = OrderedDict()
        self.__populate_disks()
        if not self.disks:
            raise PhysicalDiskException('There are no valid disks.')

    def __populate_disks(self):
        for udisk in self.udisks:
            device = udisk.get('DEVNAME')
            try:
                parted = PartedInterface(device, self.parted_path)
            except NullDiskException:
                log.debug('NullDiskException for %s' % device)
                continue
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

    def _get_parted_interface_for_allocated_device(self, disk):
        if not disk.partition_table:
            raise LayoutValidationError('Disk is not allocated')
        return PartedInterface(device=disk.devname,
                               parted_path=self.parted_path,
                               partition_start=disk.partition_table.partition_start.bytes,
                               gap=disk.partition_table.gap.bytes,
                               alignment=disk.partition_table.alignment.bytes
        )

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

    def _find_partition_devname(self, disk, partition_id):
        partitions = self.udev.find_partitions(disk.devname)
        for partition in partitions:
            if int(partition.get('UDISKS_PARTITION_NUMBER', -1)) == partition_id:
                return partition.get('DEVNAME')

    def apply(self):
        """Lots of logging here
        """
        for disk in self.allocated:
            parted = self._get_parted_interface_for_allocated_device(disk)
            partition_table = disk.partition_table
            parted.set_label(partition_table.type)
            for partition in partition_table.partitions:
                partition_id = parted.create_partition(partition.name,
                                                       partition.size.bytes,
                                                       boot_flag=partition.boot,
                                                       lvm_flag=partition.lvm)
                #  it takes some time for the uevent to register and the partition to be added
                #  to udisks. To avoid this sleep and possible race condition, we should switch
                #  to using a udev monitor which as the original design
                time.sleep(5)
                partition_name = self._find_partition_devname(disk, partition_id)
                if not partition_name:
                    log.error('%s %s %s' % (partition_name, disk, partition_id))
                    raise PhysicalDiskException('Could not relate partition id to devname')

                if partition.file_system:
                    partition.file_system.create(partition_name)
