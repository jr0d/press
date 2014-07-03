from press.models.partition import PartitionTableModel
from press.structure import EXT4, Partition, PercentString, Size, Layout, SWAP
from press.logger import setup_logging

import logging
setup_logging()

log = logging.getLogger(__name__)

disk = '/dev/loop0'

p1 = Partition('primary', PercentString('100%FREE'), file_system=EXT4('ROOT'), mount_point='/')

pm1 = PartitionTableModel('msdos', disk=disk)

pm1.add_partition(p1)

log.debug(pm1.allocated_space)

l1 = Layout(loop_only=True)

l1.add_partition_table_from_model(pm1)

log.debug(l1.disks)
log.debug(l1.disks[disk].partition_table)

l1.apply()
log.info('Apply completed!')
