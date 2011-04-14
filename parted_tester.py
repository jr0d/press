import sys
from disk_maker import Size
from parted import *


pi = PartedInterface(device='/dev/sda')
table_out = pi.get_table()

for line in table_out:
    print line



size = pi.get_size()
print size

s = Size(size)

print s.megabytes()

print 'lets remove a partition!'

print 'Using disk: %s' % pi.device
choice = raw_input('Would you like to continue? [YES/n]')

if choice != 'YES':
    print 'WINNING'
    sys.exit(0)

pi.remove_partition(1)


