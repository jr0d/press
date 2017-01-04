import logging

from press.helpers import deployment
from press.targets.linux.grub2_target import Grub2
from press.targets.linux.debian.debian_target import DebianTarget

log = logging.getLogger(__name__)



class Ubuntu1604Target(DebianTarget, Grub2):
    name = 'ubuntu_1604'
    dist = 'xenial'

    grub2_install_path = 'grub-install'
    grub2_mkconfig_path = 'grub-mkconfig'
    grub2_config_path = '/boot/grub/grub.cfg'

    def set_timezone(self, timezone):
        timezone_path = '/etc/timezone'
        localtime_path = '/etc/localtime'
        deployment.remove_file(self.join_root(timezone_path))
        deployment.remove_file(self.join_root(localtime_path))
        deployment.write(self.join_root(timezone_path), timezone)
        self.reconfigure_package('tzdata')

    def run(self):
        super(DebianTarget, self).run()
        self.localization()
        self.generate_locales()
        self.write_mdadm_configuration()
        self.write_interfaces()
        self.update_host_keys()
        self.remove_resolvconf()
        self.update_debconf_for_grub()
        self.grub_disable_recovery()
        self.install_grub2()
