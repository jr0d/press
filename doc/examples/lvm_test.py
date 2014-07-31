from press.structure.size import PercentString
from press.structure.filesystems.extended import EXT4
from press.structure.lvm import PhysicalVolume, VolumeGroup, LogicalVolume
from press.logger import setup_logging

import logging
setup_logging()

log = logging.getLogger(__name__)

pv1 = PhysicalVolume('/dev/loop0p5', size=535822336)

vg1 = VolumeGroup('vg_test', [pv1])

lv1 = LogicalVolume('lv_test1', '100MiB', EXT4('LVM'), mount_point='/lvm')
lv2 = LogicalVolume('lv_test2', PercentString('20%FREE'))
vg1.add_volumes([lv1, lv2])

print vg1