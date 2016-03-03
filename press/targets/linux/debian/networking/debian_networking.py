import logging
import os

from press.helpers import deployment
from press.targets import util

# TODO: Remove jinja2 dependency
from jinja2 import Environment

log = logging.getLogger(__name__)


def get_template_path():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_dir, 'interfaces.template')


def render_template(networks):
    template_path = get_template_path()
    if not os.path.exists(template_path):
        log.warn('Interfaces template is missing')
        return
    environment = Environment(trim_blocks=True, lstrip_blocks=True)
    with open(template_path) as fp:
        template = environment.from_string(fp.read())
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
                                                            'missing_ok', False))
        for network in networks:
            if name == network.get('interface'):
                network['device'] = device.devname
                network['type'] = network.get('type', 'AF_INET')

    deployment.write(path, render_template(networks))
