from press.exceptions import PressCriticalException

from press.images.tarball import TarImage
from press.images.wim import WimImage


_image_map = {
    'tar': TarImage,
    'tar_bz': TarImage,
    'tar_gz': TarImage,
    'tar_xz': TarImage,
    'tgz': TarImage,
    'wim': WimImage
}


def get_image_handler(image_type):
    try:
        return _image_map[image_type.lower()]
    except KeyError:
        raise PressCriticalException("Image type '{}' is not supported".format(image_type))
