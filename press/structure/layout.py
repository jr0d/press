from press.parted import PartedInterface
from press.udev import UDevHelper
from press.structure.size import Size

from .exceptions import PhysicalDiskException

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
            device = self.available_devices[idx]
            if ref == device['DEVNAME']:
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

    # def add_disk(self, disk):
    #     if not isinstance(disk, Disk):
    #         raise ValueError('Expected Disk instance.')
    #     if not self.available_devices:
    #         raise PhysicalDiskException('There are no more available devices.')
    #     if self.disk_association == 'explicit':
    #         if not disk.path:
    #             raise PhysicalDiskException('explicit lookup requires an explicit name.')
    #         idx = self._find_device_by_ref(disk.path)
    #         if idx == -1:
    #             raise PhysicalDiskException('%s is not present.' % disk.path)
    #         real_disk = self.available_devices.pop(idx)
    #     elif self.disk_association == 'first':
    #         real_disk = self.available_devices[0]
    #         self.available_devices = list()
    #     elif self.disk_association == 'any':
    #         idx = self._find_device_by_size(disk.partition_table.size)
    #         if idx == -1:
    #             raise PhysicalDiskException('No disk large enough for partition table.')
    #         real_disk = self.available_devices.pop(idx)
    #     else:
    #         raise ValueError('Unsupported association')
    #
    #     parted = PartedInterface(real_disk['DEVNAME'])
    #     size = Size(parted.get_size())
    #     disk.size = size
    #     disk.path = PartedInterface(real_disk['DEVNAME'])
    #     self.disks.append(disk)
    #

    def add_partition(self, partition):
        pass
