import logging
from press import exceptions
from press.helpers.imagefile import ImageFile
from press.hooks.hooks import run_hooks

log = logging.getLogger(__name__)

_default_chunk_size = 1048576
_default_image_format = 'tgz'
_default_hash_method = 'sha1'


def imagefile_generator(image_config, target, proxy_info=None):
    checksum_details = image_config.get('checksum')
    if checksum_details:
        image_hash = checksum_details.get('hash')
        if not image_hash:
            raise exceptions.GeneratorError('hash checksum is missing, check configuration')
        hash_method = checksum_details.get('method', _default_hash_method)
    else:
        image_hash = None
        hash_method = None

    dl = ImageFile(url=image_config['url'],
                   target=target,
                   hash_method=hash_method,
                   expected_hash=image_hash,
                   buffer_size=image_config.get('chunk_size', _default_chunk_size),
                   proxy=proxy_info)

    return dl


class ImageMixin(object):
    def __init__(self, press_configuration, deployment_root):
        self.__local_configuration = press_configuration
        self.image_configuration = self.__local_configuration.get('image')

        if not self.image_configuration:
            return

        proxy = press_configuration.get('proxy')
        self.imagefile = imagefile_generator(self.image_configuration,
                                             deployment_root,
                                             proxy)

    def fetch_image(self):
        if self.imagefile.image_exists:
            if self.imagefile.can_validate:
                log.info('Image is present on file system. Hashing image')
                self.imagefile.hash_file()
            return

        def our_callback(total, done):
            log.debug('Downloading: %.1f%%' % (float(done) / float(total) * 100))

        log.info('Starting Download...')
        self.imagefile.download(our_callback)
        log.info('done')

    def validate_image(self):
        if self.imagefile.can_validate:
            log.info('Validating image...')
            if not self.imagefile.validate():
                raise exceptions.ImageValidationException('Error validating image checksum')
            log.info('done')

    def extract_image(self):
        log.info('Extracting image')
        self.imagefile.extract()
        if not self.image_configuration.get('keep'):
            self.imagefile.cleanup()

    def run_image_ops(self):

        run_hooks('pre-image-acquire', self.__local_configuration)
        self.fetch_image()
        run_hooks('post-image-acquire', self.__local_configuration)

        run_hooks('pre-image-validate', self.__local_configuration)
        self.validate_image()
        run_hooks('post-image-validate', self.__local_configuration)

        run_hooks('pre-image-extract', self.__local_configuration)
        self.extract_image()
        run_hooks('post-image-extract', self.__local_configuration)
