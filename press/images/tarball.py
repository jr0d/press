from press.helpers.deployment import tar_extract
from press.images.imagefile import ImageFile


class TarImage(ImageFile):
    def extract(self):
        return tar_extract(self.full_filename, chdir=self.target)
