from __future__ import print_function
import logging
import sys

from press.models.partition import PartitionTableModel
from press.layout import EXT4, Partition, PercentString, Layout, SWAP
from press.chroot.debian import DebianChroot
from press.network.base import Network
from press.helpers.cli import run
from press.logger import setup_logging
from press import helpers
import yaml


try:
    yaml_file = str(sys.argv[1])
except:
    print('Please pass a path to a configuration file to run.')
    print("ex. python2.7 doc/examples/end_to_end_test.py configuration/debian7.yaml")
    sys.exit()

setup_logging()

log = logging.getLogger(__name__)



disk = '/dev/sda'

p1 = Partition('primary', '250MiB', file_system=EXT4('BOOT'), boot=True,
               mount_point='/boot')
p2 = Partition('primary', '512MiB', file_system=SWAP('SWAP'))
p3 = Partition('logical', '512MiB', file_system=EXT4(), mount_point='/tmp')
p4 = Partition('logical', PercentString('85%FREE'), file_system=EXT4('ROOT'),
               mount_point='/')

pm1 = PartitionTableModel('msdos', disk=disk)

pm1.add_partitions([p1, p2, p3, p4])

log.debug(pm1.allocated_space)

l1 = Layout(loop_only=False)

l1.add_partition_table_from_model(pm1)

log.debug(l1.disks)
log.debug(l1.disks[disk].partition_table)

l1.apply()
log.info('Apply completed!')
l1.mount_disk()
log.info('Target mount completed!')

f = open(yaml_file, 'rt')
config = yaml.load(f.read())

# From press.helpers.download.py
def my_callback(bytes_so_far):
    print('Bytes so far: %d' % bytes_so_far)

image_details = config.get('image')

url = image_details.get('url')
hash_method = image_details.get('checksum')['method']
expected_hash = image_details.get('checksum')['hash']

log.info('Starting download of image %s' % url)

dl = helpers.download.Download(url, hash_method, expected_hash, chunk_size=1024 * 1024)
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
run('mv %s/etc/fstab_rs %s/etc/fstab' % (new_root, new_root))


network = Network(new_root, config)
network.apply()

chroot = DebianChroot(new_root, config, l1.disks)
chroot.apply()
chroot.__exit__()

log.info('Done!')

