from press.models.partition import PartitionTableModel
from press.structure import EXT4, Partition, PercentString, Size, Layout

ext4 = EXT4('BOOT')
p1 = Partition('primary', '2GiB', file_system=ext4)
p2 = Partition('logical', PercentString('25%FREE'), file_system=ext4)

pm1 = PartitionTableModel('msdos', disk='/dev/loop0')

pm1.add_partitions([p1, p2])

print pm1.allocated_space

l1 = Layout()

l1.add_partition_table_from_model(pm1)

print l1.disks
print l1.disks['/dev/loop0'].partition_table