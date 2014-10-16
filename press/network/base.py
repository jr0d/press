import logging
import os
from press.helpers.file import write
from press.udev import UDevHelper

from jinja2 import Environment, FileSystemLoader

log = logging.getLogger(__name__)


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
        self.udev_helper = UDevHelper()
        log.debug('Setting up networking from configuration: %s' % self.config)

    @staticmethod
    def __generate_config(config):
        """
        Generates config by updating DEFAULTS with config.
        """
        networking = dict(networking=config.get('networking', {}))
        return networking

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

    def get_primary_ip(self):
        networks = self.config['networking']['networks']
        if networks:
            return networks[0].get('ip_address')

    def set_hostname(self):
        """
        Writes hostname.
        """
        log.debug('Running set_hostname')
        hostname = self.config['networking']['hostname']
        if hostname:
            log.info('Setting hostname: %s' % hostname)
            write('%s/etc/hostname' % self.newroot, hostname + '\n')

    def update_etc_hosts(self):
        """
        Updates /etc/hosts with a new hostname and ip
        """
        hostname = self.config['networking']['hostname']
        primary_ip = self.get_primary_ip()
        if hostname and primary_ip:
            log.info('Updating /etc/hosts')
            path = os.path.join(self.newroot, 'etc/hosts')
            hostname_short = hostname.split('.')[0]
            entry = '\n# Hostname resolver\n%s %s %s\n' % (primary_ip, hostname, hostname_short)
            write(path, entry, append=True)
        else:
            log.info('Could not determine hostname or primary ip, skipping /etc/hosts')

    def __get_interface(self, name):
        """
        Get a interface object by name.
        """
        for interface in self.config['networking']['interfaces']:
            if interface.get('name') == name:
                return interface
        log.warning('Unable to find interface by name "%s"' % name)

    def set_resolv(self):
        """

        """
        path = os.path.join(self.newroot, 'etc/resolv.conf')
        if os.path.islink(path):
            os.unlink(path)
        log.info('Writing %s' % path)
        blob = self.__render_template('resolv.template', self.config)
        write(path, blob)

    def set_interfaces(self):
        """
        Generates /etc/network/interfaces with data from config.networks
        """
        log.info('Creating interface files')
        networks = []
        for network in self.config['networking']['networks']:
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

    def set_udev_net_rules(self):
        """
        Generates /etc/udev/rules.d/##-persistent-net.rules file
        """
        log.debug("Running set_udev_net_rules")

        devices = self.udev_helper.get_network_devices()
        if not devices:
            log.warning("Couldn't find any ethernet devices")
            return

        blob = self.__render_template("persistent-net.rules.template", dict(devices=devices))
        write('%s/etc/udev/rules.d/70-persistent-net.rules' % self.newroot, blob)
        log.info("%d network interfaces were written to persistent-net.rules" % (len(devices),))

    def apply(self):
        """
        Apply network from config
        """
        log.debug('Configuring network from configuration: %s' % self.config)
        self.set_hostname()
        self.update_etc_hosts()
        self.set_resolv()
        self.set_interfaces()
        self.set_udev_net_rules()
