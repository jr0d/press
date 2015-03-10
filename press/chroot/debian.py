import logging

from press.helpers.cli import run
from press.chroot.base import Chroot
from press.helpers.file import read, replace_file


log = logging.getLogger(__name__)


class DebianChroot(Chroot):
    grub_default_path = '/etc/default/grub'

    def install_bootloader(self, disk):
        """
        Install bootloader on disk.

        :param disk: Disk as a string /dev/sda
        """
        log.debug('Setting up GRUB on %s' % disk)
        debconf = 'grub-pc grub-pc/install_devices multiselect %s' % disk
        run('echo "%s" | debconf-set-selections' % debconf,
            raise_exception=True)
        run('grub-mkconfig -o /boot/grub/grub.cfg', raise_exception=True)
        run('grub-install %s' % disk, raise_exception=True)

    @staticmethod
    def __modify_default_grub(data, appending, omitting):
        data = data.splitlines()

        # Backwards compatibility
        if isinstance(appending, (str, unicode)):
            appending = appending.split()
        if isinstance(omitting, (str, unicode)):
            omitting = omitting.split()

        for idx in xrange(len(data)):
            line = data[idx]
            if 'GRUB_CMDLINE_LINUX_DEFAULT=' in line:
                var, options = tuple(line.split('=', 1))
                options = options.strip('\"').split()
                options = [o for o in options if o not in omitting]
                options += appending
                data[idx] = '%s=\"%s\"' % (var, ' '.join(options))
                break
        return '\n'.join(data) + '\n'

    def update_grub_cmdline(self):
        bootloader_config = self.config.get('bootloader')
        cmdline_append = bootloader_config.get('cmdline_append')
        cmdline_omit = bootloader_config.get('cmdline_omit')
        if not (cmdline_append and cmdline_omit):
            log.debug('not updating linux cmdline, nothing to update')
            return
        log.info('Updating ')
        log.debug('Adding: %s, Removing: %s' % (cmdline_append, cmdline_omit))

        replace_file(self.grub_default_path,
                     self.__modify_default_grub(read(self.grub_default_path),
                                                cmdline_append,
                                                cmdline_omit))
        self.update_grub()

    @staticmethod
    def update_grub():
        log.info('Running update-grub')
        run('update-grub', raise_exception=True)

    @staticmethod
    def generate_host_keys():
        log.info('Rebuilding SSH host keys')
        run('dpkg-reconfigure openssh-server', raise_exception=False)

    @staticmethod
    def remove_resolvconf():
        log.info('Removing resolvconf package')
        run('apt-get remove resolvconf -y', raise_exception=False,
            env={'DEBIAN_FRONTEND': 'noninteractive'})

    def apply(self):
        """
        Run entire Chroot process.
        """
        self.add_users()
        bootloader_config = self.config.get('bootloader')
        if bootloader_config:
            disk = self.config['bootloader'].get('target', 'first')
            if disk == 'first':
                self.install_bootloader(self.disks.keys()[0])
            else:
                self.install_bootloader(disk)
        else:
            log.warning('Bootloader configuration is missing')

        self.update_grub_cmdline()
        self.generate_host_keys()
        self.remove_resolvconf()