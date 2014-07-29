from press.logger import setup_logging
from press.post.debian import DebianPost

import logging
setup_logging()

log = logging.getLogger(__name__)

new_root = '/dev/loop0'

post = DebianPost(new_root)
post.useradd('rack')
post.passwd('rack', 'password')

