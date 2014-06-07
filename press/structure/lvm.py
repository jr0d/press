from .size import Size
from .exceptions import LVMValidationError


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
            raise LVMValidationError(
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
