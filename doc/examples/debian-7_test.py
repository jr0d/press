from press.models.partition import PartitionTableModel
from press.structure import EXT4, Partition, PercentString, Layout, SWAP
from press.chroot.debian import DebianChroot
from press.network.base import Network
from press.cli import run
from press.logger import setup_logging
from press import helpers

import logging

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


# From press.helpers.download.py
def my_callback(bytes_so_far):
    print('Bytes so far: %d' % bytes_so_far)


log.info('Starting download of image')
dl = helpers.download.Download(
    'http://newdev.kickstart.rackspace.com/press/debian-7-wheezy-amd64.tar.gz',
    hash_method='sha1',
    expected_hash='09d2fb15faf22a76ad959371d6b72333956ef407',
    chunk_size=1024 * 1024)
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
run('mv %s/etc/fstab_rs %s/etc/fstab' % (new_root, new_root))

# A example config
config = {'auth': {'algorythim': 'sha512',
  'users': {'rack': {'gid': 1000,
    'group': 'rack',
    'home': '/home/rack',
    'password': 'ball$$$$$',
    'password_options': [{'encrypted': False}],
    'shell': '/bin/zsh',
    'skel': 'http://blah.rackspace.com/press/skels/users/rack.tar.gz',
    'uid': 1000},
   'root': {'home': '/root',
    'password': 'ball$$$$',
    'password_options': [{'encrypted': False}]}}},
 'image': {'checksum': {'hash': '3a23da7bc7636cb101a27a2f9855b427656f4775',
   'method': 'sha1'},
  'format': 'tgz',
  'url': 'http://newdev.kickstart.rackspace.com/ubuntu/testing/debian-7-wheezy-amd64.tar.gz'},
 'layout': {'loop_only': True,
  'partition_tables': [{'disk': '/dev/loop0',
    'label': 'msdos',
    'partitions': [{'file_system': {'label': 'BOOT', 'type': 'ext4'},
      'mount_point': '/boot',
      'name': 'boot',
      'options': ['primary', 'boot'],
      'size': '1GiB'},
     {'name': 'root_pv', 'options': ['logical', 'lvm'], 'size': '2GiB'}]}],
  'use_fiber_channel': False,
  'volume_groups': [{'logical_volumes': [{'file_system': {'label': 'SWAP',
       'type': 'swap'},
      'name': 'lv_swap',
      'size': '1GiB'},
     {'file_system': {'label': 'ROOT',
       'superuser_reserve': '1%',
       'type': 'ext4'},
      'mount_point': '/',
      'name': 'lv_root',
      'size': '75%FREE'}],
    'name': 'vg_system',
    'pe_szie': '4MiB',
    'physical_volumes': ['root_pv']}]},
 'network': {'dns': {'nameservers': '10.10.1.1 10.10.1.2',
   'search': ['kickstart.rackspace.com']},
  'hostname': '191676-www.kickstart.rackspace.com',
  'interfaces': [
      {'name': 'EXNET','ref': {'type': 'interface', 'value': 'eth0'}}
  ],
'networks': [{'gateway': '10.127.29.1',
'interface': 'EXNET',
'ip_address': '10.127.29.143',
'netmask': '255.255.255.0'}]},
'post': {'append': 'debug,console=ttyS01'},
'target': 'debian',
'bootloader': {'type': 'grub', 'target': '/dev/sda', 'options': 'debug,console=ttyS01'}
}

network = Network(new_root, config)
network.apply()

chroot = DebianChroot(new_root, config)
chroot.apply()
chroot.__exit__()

log.info('Done!')

