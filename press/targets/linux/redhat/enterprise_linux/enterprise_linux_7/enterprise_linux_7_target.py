import logging
import os

from press.helpers import deployment, networking as net_helper
from press.targets import GeneralPostTargetError
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

    network_scripts_path = '/etc/sysconfig/network-scripts'
    grub2_cmdline_name = 'GRUB_CMDLINE_LINUX'

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

    def write_network_script(self, device, network_config):
        script_name = 'ifcfg-%s' % device.devname
        script_path = self.join_root(os.path.join(self.network_scripts_path,  script_name))
        ip_address = network_config.get('ip_address')
        cidr_mask = net_helper.mask2cidr(network_config.get('netmask'))
        gateway = network_config.get('gateway')
        _template = networking.InterfaceTemplate(device.devname,
                                                 default_route=network_config.get('default_route', False),
                                                 ip_address=ip_address,
                                                 cidr_mask=cidr_mask,
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
            name, device = networking.lookup_interface(interface, interface.get('missing_ok', False))

            for network in networks:
                if name == network.get('interface'):
                    self.write_network_script(device, network)
                    routes = network.get('routes')
                    if routes:
                        self.write_route_script(device, routes)

    def run(self):
        super(EL7Target, self).run()
        self.rebuild_initramfs()
        self.check_for_grub()
        self.install_grub2()
        self.update_host_keys()
        self.configure_networks()
        self.write_resolvconf()
