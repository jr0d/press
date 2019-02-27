from press.generators import image


def test_imagefile_generator():
    image_config = {
        'url': 'http://localhost/image_name.tar.gz',
        'checksum':  {
            'hash': '3a23da7bc7636cb101a27a2f9855b427656f4775',
            'method': 'sha1'
        },
        'format': 'tgz'
    }
    target = 'debian'
    proxy_info = 'http://proxy:3128'

    image_handler = image.imagefile_generator(image_config, target, proxy_info)

    assert image_handler.extra['format'] == 'tgz'
    assert image_handler.__class__.__name__ == 'TarImage'

    image_config['wim_index'] = 2
    image_config['format'] = 'wim'

    image_handler = image.imagefile_generator(image_config, target, proxy_info)

    assert image_handler.__class__.__name__ == 'WimImage'
    assert image_handler.wim_index == 2
