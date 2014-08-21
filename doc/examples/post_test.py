from press.logger import setup_logging
from press.chroot.debian import DebianPost
from press.cli import run

import logging
setup_logging()

log = logging.getLogger(__name__)

new_root = '/mnt/press'
run('cp /etc/resolv.conf %s/etc/resolv.conf' % new_root)

post = DebianPost(new_root)
post.useradd('rack')
post.passwd('rack', 'password')

# Install Kernel
post.install_packages(['linux-generic'])

post.grub_install('/dev/loop')

# After we complete lets delete the Post to call __exit__ function.
post.__exit__()

