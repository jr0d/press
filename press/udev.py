"""
From the pyudev docs:

    Once added, a filter cannot be removed anymore. Create a new object instead.

pyudev can be kind of silly, but I certainly don't feel like wrapping my own.
"""

import pyudev


class UDevHelper(object):
    def __init__(self):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)

    def get_partitions(self):
        return self.context.list_devices(subsystem='block', DEVTYPE='partition')

    def get_disks(self):
        return self.context.list_devices(subsystem='block', DEVTYPE='disk')

    def find_partitions(self, device):
        """
        matches partitions belonging to a device.
        """

        devices = self.get_partitions()
        return devices.match_parent(pyudev.Device.from_device_file(self.context, device))

    def get_device_by_name(self, devname):
        try:
            udisk = pyudev.Device.from_device_file(self.context, devname)
        except OSError:
            return None
        return udisk

    def discover_valid_storage_devices(self, fc_enabled=True, loop_enabled=False):
        """
        Kind of ugly, but gets the job done. It strips devices we don't
        care about, such as cd roms, device mapper block devices, loop, and fibre channel.

        """

        disks = self.get_disks()
        pruned = list()

        for disk in disks:
            if not fc_enabled and 'fc' in disk.get('ID_BUS', ''):
                continue

            if not loop_enabled and disk.get('MAJOR') == '7':
                continue

            if disk.get('ID_TYPE') == 'cd':
                continue

            if disk.get('MAJOR') == '254':  # Device Mapper (LVM)
                continue

            pruned.append(disk)

        return pruned

    def yield_mapped_devices(self):
        disks = self.get_disks()
        for disk in disks:
            if disk.get('MAJOR') == '254':  # Device Mapper (LVM)
                yield disk

    def monitor_partition_by_devname(self, partition_id):
        self.monitor.filter_by('block', device_type="partition")
        for _, device in self.monitor:
                if device.get('UDISKS_PARTITION_NUMBER') == str(partition_id):
                    return str(device['DEVNAME'])
