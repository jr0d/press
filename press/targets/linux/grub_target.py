import logging
import os

from press.helpers import deployment
from press.targets import Target
from press.targets import util

log = logging.getLogger(__name__)


class Grub(Target):
    grub_cmdline_config_path = '/boot/grub/grub.conf'
    grub_cmdline_name = 'kernel'

    grub_install_path = 'grub-install'
    grubby_path = 'grubby'

    @property
    def bootloader_configuration(self):
        return self.press_configuration.get('bootloader')

    @property
    def kernel_parameters(self):
        return self.bootloader_configuration.get('kernel_parameters')

    @property
    def disk_targets(self):
        return self.disk_target if isinstance(self.disk_target, list) else \
                [self.disk_target]

    @property
    def disk_target(self):
        _target = self.bootloader_configuration.get('target', 'first')
        if _target == 'first':
            return list(self.layout.disks.keys())[0]
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

        full_path = self.join_root(self.grub_cmdline_config_path)
        if not os.path.exists(full_path):
            log.warn('Grub configuration is missing from image')
            return

        data = deployment.read(full_path, splitlines=True)

        modified = False
        for idx in range(len(data)):
            line = data[idx]
            line = line.strip()

            if line and line[0] == '#':
                continue

            if self.grub_cmdline_name in line:
                data[idx] = util.misc.opts_modifier(line, appending, removing, quoted=False)
                log.debug('%s > %s' % (line, data[idx]))
                modified = True
                continue

        if modified:
            log.info('Updating %s' % self.grub_cmdline_config_path)
            deployment.replace_file(full_path, '\n'.join(data) + '\n')
        else:
            log.warn('Grub configuration was not updated, no matches!')

    def install_grub(self):
        if not self.bootloader_configuration:
            log.warn('Bootloader configuration is missing')
            return

        self.update_kernel_parameters()

        log.info('Generating grub configuration')
        # TODO(mdraid): We may need run grub2-mkconfig on all targets?
        root_partition = deployment.find_root(self.layout)
        root_uuid = root_partition.file_system.fs_uuid

        kernels = os.listdir(self.join_root('/lib/modules'))
        for kernel in kernels:
            self.chroot('%s --args=root=UUID=%s --update-kernel=/boot/vmlinuz-%s' % (self.grubby_path, root_uuid, kernel))
        for disk in self.disk_targets:
            log.info('Installing grub on %s' % disk)
            self.chroot(
                '%s %s' % (self.grub_install_path, disk))
