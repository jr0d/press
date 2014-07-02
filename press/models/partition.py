from ..structure import Size
import logging

log = logging.getLogger(__name__)


class PartitionTableModel(object):
    """
    Mimics PartitionTable structured class but does not contain size attribute.
    Used to stage a partition table prior to knowing physical geometry
    """
    def __init__(self, table_type, disk='first'):
        """
        :param table_type: (str) gpt or msdos
        :param disk: (str) first, any, devname (/dev/sda), devlink (/dev/disk/by-id/foobar),
        or devpath (/sys/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda)
            first: The first available disk, regardless of size will be used
            any: Any disk that can accommodate the static allocation of the partitions
        """
        log.info('Initializing new Partition Table Model: Type: %s , Disk: %s' % (table_type, disk))
        self.partitions = list()
        self.disk = disk

        valid_types = ['gpt', 'msdos']
        if table_type not in valid_types:
            raise ValueError('table not supported: %s' % table_type)

        self.type = table_type

    def add_partition(self, partition):
        """
        :param partition: (Partition) should be compatible with a structure.disk.Partition object
        """
        self.partitions.append(partition)

    def add_partitions(self, partitions):
        """Adds partitions from iterable
        """
        for partition in partitions:
            if partition.swap:
                log.info('Adding partition: SWAP, size: %s' % partition.size)
            else:
                if partition.percent_string:
                    log.info('Adding partition: %s, size: %s' %
                           (partition.mount_point, partition.percent_string))
                else:
                    log.info('Adding partition: %s, size: %s' %
                             (partition.mount_point, partition.size))
            self.add_partition(partition)

    @property
    def allocated_space(self):
        """Return Size object of the sum of the size for statically
        allocated (not percent) partitions. I am not proud of this sentence.
        """
        size = Size(0)

        if not self.partitions:
            return size

        for part in self.partitions:
            if part.percent_string:
                continue
            size += part.size

        return size