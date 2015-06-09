import logging
import os

from press.helpers import deployment
from press.targets import Target
from press.targets.linux import util

log = logging.getLogger(__name__)


class Grub2(Target):
    grub2_cmdline_config_path = '/etc/default/grub'
    grub2_cmdline_name = 'GRUB_CMDLINE_LINUX_DEFAULT'

    grub2_install_path = 'grub2-install'
    grub2_mkconfig_path = 'grub2-mkconfig'
    grub2_config_path = '/boot/grub2/grub.cfg'

    @property
    def bootloader_configuration(self):
        return self.press_configuration.get('bootloader')

    @property
    def kernel_parameters(self):
        return self.bootloader_configuration.get('kernel_parameters')

    @property
    def disk_target(self):
        _target = self.bootloader_configuration.get('target', 'first')
        if _target == 'first':
            return self.disks.keys()[0]
        return _target

    def update_kernel_parameters(self):
        """
        A little hacktastic
        :return:
        """

        appending = self.kernel_parameters.get('append', list())
        removing = self.kernel_parameters.get('remove', list())

        if not (appending or removing):
            return

        full_path = self.join_root(self.grub2_cmdline_config_path)
        if not os.path.exists(full_path):
            log.warn('Grub configuration is missing from image')
            return

        data = deployment.read(full_path, splitlines=True)

        modified = False
        for idx in xrange(len(data)):
            line = data[idx]
            line = line.strip()

            if line and line[0] == '#':
                continue

            if self.grub2_cmdline_name in line:
                data[idx] = util.opts_modifier(line, appending, removing)
                log.debug('%s > %s' % (line, data[idx]))
                modified = True
                continue

        if modified:
            log.info('Updating %s' % self.grub2_cmdline_config_path)
            deployment.replace_file(full_path, '\n'.join(data) + '\n')
        else:
            log.warn('Grub configuration was not updated, no matches!')

    def install_grub2(self):
        if not self.bootloader_configuration:
            log.warn('Bootloader configuration is missing')
            return

        self.update_kernel_parameters()

        log.info('Generating grub configuration')
        self.chroot('%s -o %s' % (self.grub2_mkconfig_path, self.grub2_config_path))
        log.info('Installing grub on %s' % self.disk_target)
        self.chroot(
            '%s --target=i386-pc --recheck --debug %s' % (self.grub2_install_path,
                                                          self.disk_target))
