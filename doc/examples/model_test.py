from __future__ import print_function
from press.models.lvm import VolumeGroupModel
from press.models.partition import PartitionTableModel
from press.layout import EXT4, Partition, PercentString, Layout, SWAP
from press.layout.lvm import LogicalVolume, PhysicalVolume

from press.logger import setup_logging

import logging
setup_logging()

log = logging.getLogger(__name__)

disk = '/dev/loop0'

p1 = Partition('primary', '2GiB', file_system=EXT4('BOOT'), flags=['boot'], mount_point='/boot',
               fsck_option=2)
p2 = Partition('primary', '512MiB', file_system=SWAP('SWAP'), mount_point='swap')
p3 = Partition('primary', '512MiB',
               file_system=EXT4('TMP', mount_options=['defaults', 'nosuid', 'noexec', 'nodev']),
               mount_point='/tmp', fsck_option=2)
p4 = Partition('primary', PercentString('100%FREE'), flags=['lvm'])

pm1 = PartitionTableModel('msdos', disk=disk)

pm1.add_partitions([p1, p2, p3, p4])

log.debug(pm1.allocated_space)

pv1 = PhysicalVolume(p4)
vg1 = VolumeGroupModel('vg_test', [pv1])
lv1 = LogicalVolume('lv_test1', PercentString('99%FREE'),
                    file_system=EXT4('ROOT_LV'), mount_point='/',
                    fsck_option=1)
vg1.add_logical_volume(lv1)

print(vg1)

l1 = Layout(loop_only=True)

l1.add_partition_table_from_model(pm1)
print(pv1.reference.size.bytes)
l1.add_volume_group_from_model(vg1)

for vg in l1.volume_groups:
    print(vg)

log.debug(l1.disks)
log.debug(l1.disks[disk].partition_table)


l1.apply()
log.info('Apply completed!')

from pprint import pprint
pprint(l1.mount_point_index)
