import logging

from press.helpers.cli import run
from press.images.imagefile import ImageFile

log = logging.getLogger(__name__)


class WimImage(ImageFile):
    def __init__(self,
                 url,
                 target,
                 hash_method=None,
                 expected_hash=None,
                 download_directory=None,
                 buffer_size=20480,
                 proxy=None,
                 wim_index=1,
                 **extra):
        super(WimImage, self).__init__(
            url,
            target,
            hash_method,
            expected_hash,
            download_directory,
            buffer_size,
            proxy,
            **extra)
        log.debug('WimImage handler init')
        self.wim_index = wim_index

    def extract(self):
        log.info('Applying WIM to {}', self.target)
        run("wimapply {} {} {}".format(
            self.full_filename, self.wim_index, self.target), raise_exception=True)
