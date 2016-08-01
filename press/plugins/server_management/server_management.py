import logging

from press.helpers import cli
from press.plugins.server_management.omsa import OMSAUbuntu1404, OMSAUbuntu1604, OMSARHEL7, OMSARHEL6
from press.plugins.server_management.spp import SPPUbuntu1404, SPPUbuntu1604, SPPRHEL7, SPPRHEL6
from press.plugins.server_management.vmware import VMWareToolsUbuntu1404, VMWareToolsUbuntu1604, VMWareToolsEL7, VMWareToolsEL6
from press.targets.registration import register_extension



log = logging.getLogger('press.plugins.server_management')

extension_mapper = {
    'Dell Inc.': [
        OMSAUbuntu1404,
        OMSAUbuntu1604,
        OMSARHEL7,
        OMSARHEL6
    ],
    'HP': [
        SPPUbuntu1404,
        SPPUbuntu1604,
        SPPRHEL7,
        SPPRHEL6
    ],
    'VMware, Inc.': [
        VMWareToolsUbuntu1404,
        VMWareToolsUbuntu1604,
        VMWareToolsEL7,
        VMWareToolsEL6
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
    plugin_configuration = configuration.get('server_management', {})
    manufacturer = plugin_configuration.get('override_manufacturer') or get_manufacturer()
    log.info('Server manufacturer: %s' % manufacturer)

    if manufacturer == 'Dell Inc.':
        OMSAUbuntu1404.__configuration__ = configuration
        register_extension(OMSAUbuntu1404)

        OMSAUbuntu1604.__configuration__ = configuration
        register_extension(OMSAUbuntu1604)

        OMSARHEL7.__configuration__ = configuration
        register_extension(OMSARHEL7)

        OMSARHEL6.__configuration__ = configuration
        register_extension(OMSARHEL6)

    elif manufacturer == 'VMware, Inc.':
        VMWareToolsUbuntu1404.__configuration__ = configuration
        register_extension(VMWareToolsUbuntu1404)

        VMWareToolsUbuntu1604.__configuration__ = configuration
        register_extension(VMWareToolsUbuntu1604)

        VMWareToolsEL7.__configuration__ = configuration
        register_extension(VMWareToolsEL7)
    
        VMWareToolsEL6.__configuration__ = configuration
        register_extension(VMWareToolsEL6)

    elif manufacturer == 'HP':
        SPPRHEL7.__configuration__ = configuration
        register_extension(SPPRHEL7)

        SPPRHEL6.__configuration__ = configuration
        register_extension(SPPRHEL6)

        register_extension(SPPUbuntu1404)

        register_extension(SPPUbuntu1604)
