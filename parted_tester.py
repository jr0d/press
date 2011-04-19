import sys
from types import Size
from parted import *


pi = PartedInterface(device='/dev/sdc')
table_out = pi.get_table()

for line in table_out:
    print line

size = pi.get_size()
print size

s = Size(size)

print s.megabytes()

print 'lets remove a partition!'

print 'Using disk: %s' % pi.device
#choice = raw_input('Would you like to continue? [YES/n]')

#if choice != 'YES':
#    print 'WINNING'
#    sys.exit(0)

removed = pi.wipe_table()

print 'removed %s partitions!' % (removed)

print 'Creating a test partition!'

part_type = 'ext4'
part_size = Size('1G')
print part_size
print part_size.megabytes()

print 'Creating first'
pi.create_partition(part_type, part_size)
print 'Creating second'
pi.create_partition(part_type, Size('500M'))




