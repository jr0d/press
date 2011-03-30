from disk_maker import Size

size = Size('124G')

print size.humanize()
print size.bytes

size2 = Size('15G')
print size2
print size + size2

size3 = Size(size + size2)
print size3.__repr__()
print size3

print str(size3.megabytes()) + 'M'
