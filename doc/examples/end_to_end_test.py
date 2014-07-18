from press.models.partition import PartitionTableModel
from press.structure import EXT4, Partition, PercentString, Size, Layout, SWAP
from press.logger import setup_logging
from press import helpers

import logging
setup_logging()

log = logging.getLogger(__name__)

disk = '/dev/loop0'

p1 = Partition('primary', '250MiB', file_system=EXT4('BOOT'), boot=True, mount_point='/boot')
p2 = Partition('primary', '512MiB', file_system=SWAP('SWAP'))
p3 = Partition('logical', ('512MiB'), file_system=EXT4(), mount_point='/tmp')
p4 = Partition('logical', PercentString('85%FREE'), file_system=EXT4('ROOT'), mount_point='/')

pm1 = PartitionTableModel('msdos', disk=disk)

pm1.add_partitions([p1, p2, p3, p4])

log.debug(pm1.allocated_space)

l1 = Layout(loop_only=True)

l1.add_partition_table_from_model(pm1)

log.debug(l1.disks)
log.debug(l1.disks[disk].partition_table)

l1.apply()
log.info('Apply completed!')
l1.mount_disk()
log.info('Target mount completed!')


# From press.helpers.download.py
def my_callback(bytes_so_far):
    print('Bytes so far: %d' % bytes_so_far)

log.info('Starting download of image')
dl = helpers.download.Download('http://cdimage.ubuntu.com/ubuntu-core/releases/trusty/release/ubuntu-core-14.04-core-amd64.tar.gz', hash_method='sha1', expected_hash='ce3ad2ae205f5a90759d0a57b8cd90e687b4af1d', chunk_size=1024*1024)
dl.download(my_callback)
if dl.can_validate():
    print('Can do validation..')
    if dl.validate():
        print('Checksums match up!')
    else:
        print('Checksums do NOT MATCH!')
else:
    print("Validation can't be performed")

log.info('Extracting image.')
dl.extract('/mnt/press')
log.info('Done!')

