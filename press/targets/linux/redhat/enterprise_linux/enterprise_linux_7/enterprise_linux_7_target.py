import logging
import os

import ipaddress

from press.helpers import deployment, networking as net_helper
from press.targets import GeneralPostTargetError
from press.targets import util
from press.targets.linux.grub2_target import Grub2
from press.targets.linux.redhat.enterprise_linux.enterprise_linux_target \
    import EnterpriseLinuxTarget
from press.targets.linux.redhat.enterprise_linux.enterprise_linux_7 \
    import networking


log = logging.getLogger(__name__)


class EL7Target(EnterpriseLinuxTarget, Grub2):
    """
    Should work with CentOS and RHEL.
    """
    name = 'enterprise_linux_7'

    network_file_path = '/etc/sysconfig/network'
    network_scripts_path = '/etc/sysconfig/network-scripts'

    def check_for_grub(self):
        _required_packages = ['grub2', 'grub2-tools']
        if not self.packages_exist(_required_packages):
            if not self.install_packages(_required_packages):
                raise GeneralPostTargetError('Error installing required packages for grub2')

    def rebuild_initramfs(self):
        if not self.package_exists('dracut-config-generic'):
            self.install_package('dracut-config-generic')

        kernels = os.listdir(self.join_root('/usr/lib/modules'))
        for kernel in kernels:
            initramfs_path = '/boot/initramfs-%s.img' % kernel
            if os.path.exists(self.join_root(initramfs_path)):
                log.info('Rebuilding %s' % initramfs_path)
                self.chroot('dracut -v -f %s %s' % (initramfs_path, kernel))

    def enable_ipv6(self):
        with open(self.join_root(self.network_file_path)) as f:
            contents = f.read()
        if "NETWORKING_IPV6" in contents:
            if "NETWORKING_IPV6=NO" in contents:
                contents.replace("NETWORKING_IPV6=NO", "NETWORKING_IPV6=YES")
            else:
                return
        else:
            contents += "\nNETWORKING_IPV6=YES\n"
        log.info("Enabling IPv6 in {}".format(self.network_file_path))
        with open(self.join_root(self.network_file_path), "w") as f:
            f.write(contents)

    def write_network_script(self, device, network_config, dummy=False):
        script_name = 'ifcfg-%s' % device.devname
        script_path = self.join_root(os.path.join(self.network_scripts_path,  script_name))
        if dummy:
            _template = networking.DummyInterfaceTemplate(device.devname)
        else:
            if network_config.get('type', 'AF_INET') == 'AF_INET6':
                self.enable_ipv6()
                interface_template = networking.IPv6InterfaceTemplate
            else:
                interface_template = networking.InterfaceTemplate

            ip_address = network_config.get('ip_address')
            gateway = network_config.get('gateway')
            prefix = network_config.get('prefix')
            if not prefix:
                prefix = ipaddress.ip_network("{ip_address}/{netmask}".format(
                    **network_config).decode("utf-8"), strict=False).prefixlen

            _template = interface_template(device.devname,
                                           default_route=network_config.get('default_route', False),
                                           ip_address=ip_address,
                                           prefix=prefix,
                                           gateway=gateway)
        log.info('Writing %s' % script_path)
        deployment.write(script_path, _template.generate())

    def write_route_script(self, device, routes):
        script_name = 'route-%s' % device.devname
        script_path = self.join_root(os.path.join(self.network_scripts_path,  script_name))
        log.info('Writing %s' % script_path)
        deployment.write(script_path, networking.generate_routes(routes))

    def configure_networks(self):
        network_configuration = self.press_configuration.get('networking')
        if not network_configuration:
            log.warn('Network configuration is missing')
            return

        interfaces = network_configuration.get('interfaces', list())
        networks = network_configuration.get('networks')
        for interface in interfaces:
            name, device = util.networking.lookup_interface(interface, interface.get('missing_ok', False))

            for network in networks:
                if name == network.get('interface'):
                    self.write_network_script(device, network, dummy=network.get('dummy', False))
                    routes = network.get('routes')
                    if routes:
                        self.write_route_script(device, routes)

    def run(self):
        super(EL7Target, self).run()
        self.localization()
        self.update_host_keys()
        self.configure_networks()
        self.rebuild_initramfs()
        self.check_for_grub()
        self.install_grub2()
