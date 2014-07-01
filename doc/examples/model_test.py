import logging
import logging.config

from press.models.partition import PartitionTableModel
from press.structure import EXT4, Partition, PercentString, Size, Layout, SWAP
from press.logger import *
import logging
## JUST SETTING UP LOGGING FOR TESTING. LIBRARIES SHOULDN'T DO THIS.
setup_logging()

log = logging.getLogger(__name__)

disk = '/dev/loop0'

p1 = Partition('primary', '2GiB', file_system=EXT4('BOOT'), boot=True, mount_point='/boot')
p2 = Partition('primary', '512MiB', swap=True, file_system=SWAP('SWAP'))
p3 = Partition('logical', PercentString('25%FREE'), file_system=EXT4('ROOT'), mount_point='/')

pm1 = PartitionTableModel('msdos', disk=disk)

pm1.add_partitions([p1, p2, p3])

log.debug(pm1.allocated_space)

l1 = Layout(loop_only=True)

l1.add_partition_table_from_model(pm1)

log.debug(l1.disks)
log.debug(l1.disks[disk].partition_table)

l1.apply()
log.info('Apply completed!')
