from disk_maker import Size, Partition, Layout

size = Size('124G')

print size.humanize()
print size.bytes

size2 = Size('15G')
print size2
print size + size2

size3 = size + size2
print size3.__repr__()
print size3

print str(size3.megabytes()) + 'M'

part_root = Partition(name='root', fs_type='ext4', size='130G')

print part_root

print 'Making test Layout:\n'

layout = Layout(disk_size='256G', table='gpt')
part_boot = Partition('boot', 'ext3', '500M')
part_tmp = Partition('tmp', 'ext3', '2G')
part_opt = Partition('opt', 'ext4', '100G')

layout.add_partition(part_boot)
layout.add_partition(part_tmp)
layout.add_partition(part_root)
layout.add_partition(part_opt)

print '%s / %s' % (layout.get_used_size(), layout.disk_size)
for elm in layout._enum_partitions():
    print elm


print layout
