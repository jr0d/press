import logging
import logging.config

from press.models.partition import PartitionTableModel
from press.structure import EXT4, Partition, PercentString, Size, Layout, SWAP

FORMAT = "%(asctime)s - %(levelname)s : %(name)s - %(message)s"
config_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': FORMAT},
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/console.out',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True,
        },
        'press.cli': {
            'handlers': ['debug'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
logging.config.dictConfig(config_dict)

log = logging.getLogger(__name__)

disk = '/dev/loop0'

p1 = Partition('primary', '2GiB', file_system=EXT4('BOOT'), boot=True, mount_point='/boot')
p2 = Partition('primary', '512MiB', swap=True, file_system=SWAP('SWAP'))
p3 = Partition('logical', PercentString('25%FREE'), file_system=EXT4(), mount_point='/')

pm1 = PartitionTableModel('msdos', disk=disk)

pm1.add_partitions([p1, p2, p3])

log.info(pm1.allocated_space)

l1 = Layout(loop_only=True)

l1.add_partition_table_from_model(pm1)

log.info(l1.disks)
log.info(l1.disks[disk].partition_table)

l1.apply()
log.info('Apply completed!')