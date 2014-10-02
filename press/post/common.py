import os
from press.helpers.file import write


def create_fstab(fstab, target):
    path = os.path.join(target, 'etc/fstab')
    write(path, fstab)