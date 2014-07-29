from press.logger import setup_logging
from press.post.debian import DebianPost

import logging
setup_logging()

log = logging.getLogger(__name__)

new_root = '/mnt/press'

post = DebianPost(new_root)
post.useradd('rack')
post.passwd('rack', 'password')

# After we complete lets delete the Post to call __exit__ function.
post.__exit__()

