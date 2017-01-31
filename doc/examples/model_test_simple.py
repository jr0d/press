from press.models.lvm import VolumeGroupModel
from press.models.partition import PartitionTableModel
from press.layout import EXT4, Partition, PercentString, Layout, SWAP
from press.layout.lvm import LogicalVolume, PhysicalVolume

from press.logger import setup_logging

import logging
setup_logging()

log = logging.getLogger(__name__)

disk = '/dev/loop0'

p1 = Partition('primary', '1MiB', mount_point='/boot')
p2 = Partition('primary', '1MiB')
p3 = Partition('primary', '512MiB')

p4 = Partition('logical', PercentString('100%FREE'))

pm1 = PartitionTableModel('msdos', disk=disk)

pm1.add_partitions([p1, p2, p3, p4])

log.debug(pm1.allocated_space)

l1 = Layout(loop_only=True)

l1.add_partition_table_from_model(pm1)

log.debug(l1.disks)
log.debug(l1.disks[disk].partition_table)


l1.apply()
log.info('Apply completed!')

from pprint import pprint
pprint(l1.mount_point_index)