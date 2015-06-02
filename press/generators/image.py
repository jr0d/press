from press.layout.exceptions import GeneratorError
from press.helpers.download import Download


_default_chunk_size = 1048576
_default_image_format = 'tgz'
_default_hash_method = 'sha1'


def downloader_generator(image_config, target, proxy_info=None):
    checksum_details = image_config.get('checksum')
    if checksum_details:
        image_hash = checksum_details.get('hash')
        if not image_hash:
            raise GeneratorError('hash checksum is missing, check configuration')
        hash_method = checksum_details.get('method', _default_hash_method)
    else:
        image_hash = None
        hash_method = None

    proxy = None
    if proxy_info:
        try:
            proxy_address = proxy_info['address']
            proxy_port = proxy_info['port']
        except KeyError as k:
            raise GeneratorError('%s is missing from proxy_info' % k.message)
        proxy = '%s:%s' % (proxy_address, proxy_port)

    dl = Download(url=image_config['url'],
                  hash_method=hash_method,
                  expected_hash=image_hash,
                  download_directory=target,
                  filename=image_config.get('filename'),
                  chunk_size=image_config.get('chunk_size', _default_chunk_size),
                  proxy=proxy)

    return dl
