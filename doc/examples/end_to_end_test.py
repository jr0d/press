from press.models.partition import PartitionTableModel
from press.structure import EXT4, Partition, PercentString, Layout, SWAP
from press.post.debian import DebianPost
from press.cli import run
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
dl = helpers.download.Download(
    'http://newdev.kickstart.rackspace.com/ubuntu/testing/debian-7-wheezy-amd64.tar.gz',
    hash_method='sha1', expected_hash='3a23da7bc7636cb101a27a2f9855b427656f4775', chunk_size=1024*1024)
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

new_root = '/mnt/press'

dl.extract(new_root)

# Nessy adding some POST action
run('cp /etc/resolv.conf %s/etc/resolv.conf' % new_root)

post = DebianPost(new_root)
post.useradd('rack')
post.passwd('rack', 'password')

post.grub_install('/dev/loop0')

# After we complete lets delete the Post to call __exit__ function.
post.__exit__()

log.info('Done!')

