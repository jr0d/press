
class PartitionTableModel(object):
    """
    Mimics PartitionTable structured class but does not contain size attribute.
    Used to stage a partition table prior to knowing physical geometry
    """
    def __init__(self, table_type):
        self.partitions = list()

        valid_types = ['gpt', 'msdos']
        if table_type not in valid_types:
            raise ValueError('table not supported: %s' % table_type)

        self.type = table_type

    def add_partition(self, partition):
        """
        partition should be compatible with a structure.disk.Partition object
        """
        self.partitions.append(partition)