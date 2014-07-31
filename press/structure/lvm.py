import logging

from press.structure import Size, PercentString
from press.structure.exceptions import LVMValidationError

log = logging.getLogger(__name__)


class PhysicalVolume(object):
    def __init__(self, devname, size):
        self.devname = devname
        self.size = Size(size)


class VolumeGroup(object):
    """
    """
    logical_volumes = list()

    def __init__(self, name, physical_volumes, pe_size=4194304):
        self.name = name
        self.physical_volumes = physical_volumes
        self.pv_raw_size = Size(sum([pv.size.bytes for pv in self.physical_volumes]))
        self.pe_size = Size(pe_size)
        self.extents = self.pv_raw_size.bytes / self.pe_size.bytes
        self.size = Size(self.pe_size.bytes * self.extents)

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
        return self.current_usage.bytes / self.pe_size.bytes

    @property
    def free_space(self):
        return self.size - self.current_usage

    @property
    def free_pe(self):
        return self.free_space.bytes / self.pe_size.bytes

    def convert_percent_to_size(self, percent, free):
        if free:
            return self.get_percentage_of_free_space(percent)
        return self.get_percentage_of_usable_space(percent)

    def _validate_volume(self, volume):
        if not isinstance(volume, LogicalVolume):
            return ValueError('Expected LogicalVolume instance')
        if self.free_space < volume.size:
            raise LVMValidationError('There is not enough space for volume: avail: %s, size: %s' % (
                self.free_space, volume.size))

    def add_volume(self, volume):
        if volume.percent_string:
            volume.size = self.convert_percent_to_size(volume.percent_string.value,
                                                       volume.percent_string.free)
        self._validate_volume(volume)
        self.logical_volumes.append(volume)

    def add_volumes(self, volumes):
        for volume in volumes:
            self.add_volume(volume)

    def get_percentage_of_free_space(self, percent):
        return Size(self.free_space.bytes * percent)

    def get_percentage_of_usable_space(self, percent):
        return Size(self.size.bytes * percent)

    def __repr__(self):
        out = 'VG: %s\nPV(s): %s\nPE/LE: %d\nPE/LE Size: %s' \
              '\nSize: %s (Unusable: %s)\nUsed: %s / %d\nAvailable: %s / %d' \
              '\nLV(s): %s' % (
                  self.name,
                  str([pv.devname for pv in self.physical_volumes]),
                  self.extents,
                  self.pe_size,
                  self.size,
                  self.pv_raw_size % self.pe_size,
                  self.current_usage,
                  self.current_pe,
                  self.free_space,
                  self.free_pe,
                  [(lv.name, str(lv.size)) for lv in self.logical_volumes]
              )
        return out


class LogicalVolume(object):
    """
    Very similar to Partition, device is the /dev/link after the device is created.
    """
    device = None

    def __init__(self, name, size_or_percent, file_system=None, mount_point=None, fsck_option=0):
        self.name = name
        if isinstance(size_or_percent, PercentString):
            self.size = None
            self.percent_string = size_or_percent
        else:
            self.size = Size(size_or_percent)
            self.percent_string = None

        self.file_system = file_system
        self.mount_point = mount_point
        self.fsck_option = fsck_option
