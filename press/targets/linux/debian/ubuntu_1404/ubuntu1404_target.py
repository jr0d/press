import logging

from press.targets.linux.grub2_target import Grub2
from press.targets.linux.debian.debian_target import DebianTarget

log = logging.getLogger(__name__)


class Ubuntu1404Target(DebianTarget, Grub2):
    name = 'ubuntu_1404'

    grub2_install_path = 'grub-install'
    grub2_mkconfig_path = 'grub-mkconfig'
    grub2_config_path = '/boot/grub/grub.cfg'

    def remove_resolvconf(self):
        log.info('Removing resolvconf package')
        self.remove_package('resolvconf')

    def update_debconf_for_grub(self):
        log.info('Updating debconf for grub')
        debconf = 'grub-pc grub-pc/install_devices multiselect %s' % self.disk_target
        self.chroot('echo %s | debconf-set-selections' % debconf)

    def run(self):
        super(DebianTarget, self).run()
        self.write_interfaces()
        self.update_host_keys()
        self.remove_resolvconf()
        self.update_debconf_for_grub()
        self.install_grub2()
        self.write_resolvconf()
