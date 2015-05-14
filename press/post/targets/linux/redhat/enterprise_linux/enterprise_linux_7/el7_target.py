import logging
import os
import shlex
from press.helpers import deployment
from press.post.targets import GeneralPostTargetError
from press.post.targets.linux.redhat.enterprise_linux.enterprise_linux_target \
    import EnterpriseLinuxTarget

log = logging.getLogger(__name__)


class EL7Target(EnterpriseLinuxTarget):
    name = 'el7'

    grub_cmdline_config_path = '/etc/sysconfig/grub'

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

        mod_count = 0
        for idx in xrange(len(data)):
            line = data[idx]
            line = line.strip()

            if mod_count >= 2:
                break

            if line and line[0] == '#':
                continue
            # Remove cmdline_omit from default options, if they exist
            if 'GRUB_CMDLINE_LINUX_DEFAULT=' in line:
                data[idx] = modifier(line, add=False)
                log.debug('%s > %s' % (line, data[idx]))
                mod_count += 1
                continue

            # Add and omit from custom cmdline options
            if 'GRUB_CMDLINE_LINUX=' in line:
                data[idx] = modifier(line, add=True)
                log.debug('%s > %s' % (line, data[idx]))
                mod_count += 1
                continue

        if mod_count:
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

    def run(self):
        super(EL7Target, self).run()
        self.install_grub2()

