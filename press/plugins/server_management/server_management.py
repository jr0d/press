import logging

from press.helpers import cli
from press.plugins.server_management.omsa import OMSAUbuntu1404
from press.targets.registration import register_extension


log = logging.getLogger('press.plugins.server_management')

extension_mapper = {
    'Dell Inc.': [
        OMSAUbuntu1404
    ]
}

def get_manufacturer():
    res = cli.run('dmidecode -s system-manufacturer', raise_exception=True)

    for line in res.splitlines():
        if line.lstrip().startswith('#'):
            continue
        return line.strip()


def plugin_init(configuration):
    log.info('Registering Server Management plugins')
    manufacturer = get_manufacturer()
    log.info('Server manufacturer: %s' % manufacturer)
    if manufacturer == 'Dell Inc.':
        OMSAUbuntu1404.__configuration__ = configuration
        register_extension(OMSAUbuntu1404)
