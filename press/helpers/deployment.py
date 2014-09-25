from press.cli import run


def mount(argument):
    run('mount %s' % argument)
    pass


def mount_root():
    run('mount -T /mnt/press_fstab /mnt/press')


def mkdir(directory):
    run('mkdir -p %s' % directory)
    pass


def mount_disk():
    pass

