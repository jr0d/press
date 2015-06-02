from pprint import pprint
import sys

from press.parted import PartedInterface
from press.layout import Size

pi = PartedInterface(device='/dev/loop0')
#if not pi.has_label:
#    print 'missing label, creating one.'
#    pi.set_label('msdos')
#

print pi.get_label()

pprint(pi.device_info)

pprint(pi.partitions)

print pi.wipe_table()

pi.set_label('msdos')

print pi.create_partition('primary', Size('25MiB').bytes, flags=['boot'])
print pi.create_partition('primary', Size('25MiB').bytes)
print pi.create_partition('primary', Size('25MiB').bytes)
print pi.create_partition('logical', Size('25MiB').bytes)
print pi.create_partition('logical', Size('25MB').bytes)

print pi.partitions

raw_input('press a key')

print pi.wipe_table()

pi.set_label('gpt')

print pi.create_partition('p1', Size('25MiB').bytes, flags=['boot'])
print pi.create_partition('p2', Size('25MiB').bytes)
print pi.create_partition('p3', Size('25MiB').bytes)
print pi.create_partition('p4', Size('25MB').bytes)
print pi.create_partition('p5', Size('25MiB').bytes)

print pi.partitions