import logging

from press.helpers import cli
from press.plugins.server_management.omsa import OMSAUbuntu1404, OMSARHEL7
from press.plugins.server_management.spp import SPPUbuntu1404, SPPRHEL7
from press.plugins.server_management.vmware import VMWareTools, VMWareToolsEL7
from press.targets.registration import register_extension


log = logging.getLogger('press.plugins.server_management')

extension_mapper = {
    'Dell Inc.': [
        OMSAUbuntu1404,
        OMSARHEL7
    ],
    'HP': [
        SPPUbuntu1404,
        SPPRHEL7
    ],
    'VMware, Inc.': [
        VMWareTools,
        VMWareToolsEL7
    ]
}

def get_os_release_value(self, key):
        """
        parses /etc/os_release and returns the key value passed in
        """
        os_release = self.target.parse_os_release()
        value = os_release.get(key)
        return value

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
        OMSARHEL7.__configuration__ = configuration
        register_extension(OMSARHEL7)

        OMSAUbuntu1404.__configuration__ = configuration
        register_extension(OMSAUbuntu1404)

    elif manufacturer == 'VMware, Inc.':
        VMWareTools.__configuration__ = configuration
        register_extension(VMWareTools)

        VMWareToolsEL7.__configuration__ = configuration
        register_extension(VMWareToolsEL7)
    
    elif manufacturer == 'HP':
        SPPRHEL7.__configuration__ = configuration
        register_extension(SPPRHEL7)

        register_extension(SPPUbuntu1404)
