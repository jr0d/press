import logging
import os
from press.helpers.file import read, write

from jinja2 import Environment, FileSystemLoader

log = logging.getLogger(__name__)

DEFAULTS = \
    {'network':
         {
             'dns': {},
             'hostname': None,
             'networks': [
                 {}
             ],
             'interfaces': [
                 {}
             ],
         }
    }


class Network(object):
    """
    Base Network Object.
    """

    def __init__(self, newroot, config):
        """
        Base constructor.
        """
        if not config.get('target'):
            raise Exception('target is required in configuration.')

        self.target = config['target']

        self.newroot = newroot
        self.config = self.__generate_config(config)
        log.debug('Setting up networking from configuration: %s' % self.config)

    @staticmethod
    def __generate_config(config):
        """
        Generates config by updating DEFAULTS with config.
        """
        network = dict(network=config.get('network', {}))
        DEFAULTS.update(network)
        return DEFAULTS

    def __render_template(self, filename, data):
        """
        Renders a jinja template with data using self.get_target
        to find template paths.
        """
        path = os.path.dirname(os.path.abspath(__file__))
        loader = FileSystemLoader(
            os.path.join(path, 'templates/%s/' % self.target))
        environment = Environment(
            trim_blocks=True, lstrip_blocks=True, loader=loader)
        return environment.get_template(filename).render(data)

    def get_target(self):
        """
        Get the target from config, this is required to render
        the correct templates.
        """
        return self.config.get('target')

    def get_hostname(self):
        """
        Gets the hostname from file.
        """
        return read('%s/etc/hostname' % self.newroot).strip()

    def set_hostname(self):
        """
        Writes hostname.
        """
        log.debug('Running set_hostname')
        hostname = self.config['network']['hostname']
        if hostname:
            log.info('Updating /etc/hostname "%s"' % hostname)
            old = self.get_hostname()
            write('%s/etc/hostname' % self.newroot, hostname)
            self.__update_hosts(old, hostname)

    def __update_hosts(self, old, new):
        """
        Updates /etc/hosts with a new hostname
        """
        log.info('Replacing %s with %s in /etc/hosts' % (old, new))
        hosts = read('%s/etc/hostname' % self.newroot)
        hosts.replace(old, new)
        write('%s/etc/hosts' % self.newroot, hosts)

    def __get_interface(self, name):
        """
        Get a interface object by name.
        """
        for interface in self.config['network']['interfaces']:
            if interface.get('name') == name:
                return interface
        log.warning('Unable to find interface by name "%s"' % name)

    def set_resolve(self):
        """
        Generate /etc/resolve with data from config.network.dns
        """
        log.debug('Running set_resolve')
        blob = self.__render_template('resolv.template', self.config)
        write('%s/etc/resolv.conf' % self.newroot, blob)

    def set_interfaces(self):
        """
        Generates /etc/network/interfaces with data from config.networks
        """
        log.debug('Running set_interfaces')
        networks = []
        for network in self.config['network']['networks']:
            interface_name = network.get('interface')
            interface = self.__get_interface(interface_name)

            if interface:
                # TODO need to check ref.type and create file accordingly.
                value = interface['ref']['value']
                if value:
                    network['interface'] = value
                    networks.append(network)
                else:
                    log.warning('interface configuration missing value.')

        data = dict(networks=networks)
        blob = self.__render_template('interfaces.template', data)
        write('%s/etc/network/interfaces' % self.newroot, blob)

    def apply(self):
        """
        Apply network from config
        """
        log.debug('Configuring network from configuration: %s' % self.config)
        self.set_hostname()
        self.set_resolve()
        self.set_interfaces()
