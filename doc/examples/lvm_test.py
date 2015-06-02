from press.layout import Partition
from press.layout.size import PercentString
from press.layout.filesystems.extended import EXT4
from press.layout.lvm import PhysicalVolume, VolumeGroup, LogicalVolume
from press.logger import setup_logging

import logging
setup_logging()

log = logging.getLogger(__name__)
partition = Partition('logical', size_or_percent='511MiB', lvm=True)
partition.devname = '/dev/loop0p5'
pv1 = PhysicalVolume(partition)

vg1 = VolumeGroup('vg_test', [pv1])

lv1 = LogicalVolume('lv_test1', '100MiB', EXT4('LVM'), mount_point='/lvm')
lv2 = LogicalVolume('lv_test2', PercentString('20%FREE'))
lv3 = LogicalVolume('lv_test3', PercentString('100%FREE'))

vg1.add_logical_volumes([lv1, lv2, lv3])

print vg1