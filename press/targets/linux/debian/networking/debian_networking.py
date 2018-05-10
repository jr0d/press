import logging

from press.helpers import deployment
from press.targets import util
from press.targets.linux.debian.networking.interfaces_template import \
    INTERFACES_TEMPLATE


# TODO: Remove jinja2 dependency
from jinja2 import Environment

log = logging.getLogger(__name__)


def render_template(networks):
    environment = Environment(trim_blocks=True, lstrip_blocks=True)
    template = environment.from_string(INTERFACES_TEMPLATE)
    log.debug('Rendering: %s' % networks)
    data = template.render(dict(networks=networks))
    log.debug('Write:\n%s' % data)
    return data


def write_interfaces(path, network_configuration):
    interfaces = network_configuration.get('interfaces', list())
    networks = network_configuration.get('networks')

    for interface in interfaces:
        name, device = util.networking.lookup_interface(interface,
                                                        interface.get(
                                                            'missing_ok',
                                                            False))
        for network in networks:
            if name == network.get('interface'):
                network['device'] = device.devname
                network['type'] = network.get('type', 'AF_INET')

    deployment.write(path, render_template(networks))
