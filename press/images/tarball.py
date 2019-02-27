from press.helpers.deployment import tar_extract
from press.images.imagefile import ImageFile


class TarImage(ImageFile):
    image_types = ['tgz', 'tar_xz']