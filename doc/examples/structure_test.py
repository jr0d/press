from press.layout import Size, Layout, Disk, PartitionTable, Partition, EXT4, PercentString


s1 = Size(19674)

print s1

print s1.humanize

s2 = Size('1.5GiB')
print s2.bytes
print s2.humanize

s3 = Size(14)

s4 = s2 + s3
print s4.bytes


disk = Disk('/dev/loop0', size='20GiB')
table1 = PartitionTable('gpt', size=disk.size.bytes)
disk.partition_table = table1

ext4 = EXT4('BOOT')
p1 = Partition('primary', '4GiB', file_system=ext4)
p2 = Partition('logical', PercentString('25%FREE'), file_system=ext4)

table1.add_partition(p1)
table1.add_partition(p2)

print table1.current_usage
print table1.free_space

print table1

print table1.partitions[1].size.bytes
print disk.partition_table.partitions[1].size.bytes

layout = Layout(loop_only=True)

print layout.disks[0].devname