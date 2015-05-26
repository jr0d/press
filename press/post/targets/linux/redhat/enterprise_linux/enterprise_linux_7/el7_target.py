import logging
import os
import shlex

from press.helpers import deployment, networking as net_helper
from press.post.targets import GeneralPostTargetError
from press.post.targets.linux.redhat.enterprise_linux.enterprise_linux_target \
    import EnterpriseLinuxTarget
from press.post.targets.linux.redhat.enterprise_linux.enterprise_linux_7 \
    import networking

log = logging.getLogger(__name__)


class EL7Target(EnterpriseLinuxTarget):
    name = 'el7'

    grub_cmdline_config_path = '/etc/default/grub'
    network_scripts_path = '/etc/sysconfig/network-scripts'

    def update_kernel_parameters(self, kernel_parameters):
        """
        A little hacktastic
        :return:
        """

        appending = kernel_parameters.get('append', list())
        removing = kernel_parameters.get('remove', list())

        if not (appending or removing):
            return

        full_path = self.join_root(self.grub_cmdline_config_path)
        if not os.path.exists(full_path):
            log.warn('Grub configuration is missing from image')
            return

        data = deployment.read(full_path, splitlines=True)

        def modifier(l, add=False):
            config_line = l.split('=', 1)
            if not len(config_line) > 1:
                var = config_line[0]
                options = '\"\"'
            else:
                var, options = tuple(l.split('=', 1))
            if options.startswith('"') and options.endswith('"'):
                options = options[1:-1]
            options = shlex.split(options)
            options = [o for o in options if o not in removing]
            if add and appending:
                options += appending

            return '%s=\"%s\"' % (var, ' '.join(options))

        modified = False
        for idx in xrange(len(data)):
            line = data[idx]
            line = line.strip()

            if line and line[0] == '#':
                continue

            if 'GRUB_CMDLINE_LINUX=' in line:
                data[idx] = modifier(line, add=True)
                log.debug('%s > %s' % (line, data[idx]))
                modified = True
                continue

        if modified:
            log.info('Updating %s' % self.grub_cmdline_config_path)
            deployment.replace_file(full_path, '\n'.join(data) + '\n')
        else:
            log.warn('Grub configuration was not updated, no matches!')

    def install_grub2(self):
        boot_loader_config = self.press_configuration.get('bootloader')
        if not boot_loader_config:
            log.warn('Bootloader configuration is missing')
            return

        _required_packages = ['grub2', 'grub2-tools']
        if not self.packages_exist(_required_packages):
            if not self.install_pacakges(_required_packages):
                raise GeneralPostTargetError('Error installing required packages for grub2')

        kernel_parameters = boot_loader_config.get('kernel_parameters')
        if kernel_parameters:
            self.update_kernel_parameters(kernel_parameters)

        _target = boot_loader_config.get('target', 'first')
        if _target == 'first':
            disk = self.disks.keys()[0]
        else:
            disk = _target

        log.info('Generating grub configuration')
        self.chroot('grub2-mkconfig -o /boot/grub2/grub.cfg')
        log.info('Installing grub on %s' % disk)
        self.chroot('grub2-install --target=i386-pc --recheck --debug %s' % disk)

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
        network_configuration = self.press_configuration.get('network')
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
        self.install_grub2()
        self.configure_networks()
        self.write_resolvconf()

