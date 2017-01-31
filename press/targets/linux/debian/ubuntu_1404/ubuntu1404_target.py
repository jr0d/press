import logging

from press.helpers import deployment
from press.targets.linux.grub2_target import Grub2
from press.targets.linux.debian.debian_target import DebianTarget

log = logging.getLogger(__name__)



class Ubuntu1404Target(DebianTarget, Grub2):
    name = 'ubuntu_1404'
    dist = 'trusty'

    grub2_install_path = 'grub-install'
    grub2_mkconfig_path = 'grub-mkconfig'
    grub2_config_path = '/boot/grub/grub.cfg'

    def create_default_locale(self):
        language = self.press_configuration.get('localization', {}).get('language', 'C')
        _locale = 'LANG=%s\nLC_MESSAGES=C\n' % language
        deployment.write(self.join_root('/etc/default/locale'), _locale)


    def run(self):
        super(DebianTarget, self).run()
        # Canonical is now setting locale in the image, so commenting out this call
        #self.create_default_locale()
        self.localization()
        self.generate_locales()
        self.write_mdadm_configuration()
        self.write_interfaces()
        self.update_host_keys()
        self.remove_resolvconf()
        self.update_debconf_for_grub()
        self.grub_disable_recovery()
        self.install_grub2()
