import logging
import os
from press.helpers import deployment
from press.targets.target_base import TargetExtension

pgp_key_file = 'dell_key.1285491434D8786F'

log = logging.getLogger('press.plugins.server_management')


class OMSADebian(TargetExtension):
    dist = ''
    mirrorbase = 'http://mirror.rackspace.com/dell/community/ubuntu'
    component = 'openmanage'

    def write_sources(self):
        log.info('Creating OMSA sources file')
        sources_path = self.join_root('/etc/apt/sources.list.d/dell-omsa.list')
        source = 'deb %s %s %s\n' % (OMSADebian.mirrorbase, self.dist, self.component)
        deployment.write(sources_path, source)

    def import_key(self):
        key_file_path = os.path.join(os.path.dirname(__file__), pgp_key_file)
        key_data = deployment.read(key_file_path)
        destination = os.path.join(self.join_root(self.target.chroot_staging_dir),
                                   pgp_key_file)
        deployment.write(destination, key_data)
        log.info('Importing Dell public key')
        self.target.chroot('apt-key add %s' % os.path.join(self.target.chroot_staging_dir,
                                                           pgp_key_file))

    def install_openipmi(self):
        self.target.install_package('openipmi')

    def install_openmanage(self):
        self.target.install_package('srvadmin-all')

    def run(self):
        self.write_sources()
        self.import_key()
        self.target.apt_update()
        self.install_openipmi()
        self.install_openmanage()


class OMSAUbuntu1404(OMSADebian):
    __extends__ = 'ubuntu_1404'
    dist = 'trusty'

class OMSAUbuntu1604(OMSADebian):
    __extends__ = 'ubuntu_1604'
    # Will be using trusty repos since Dell doesn't have xenial yet.
    dist = 'trusty'
    # specifying version 8.30
    component = 'openmanage/830'
    # Also needs a repo for Java 7
    add_java_apt_repo = "add-apt-repository -y ppa:openjdk-r/ppa"

    def write_sources(self):
        log.info('Adding Java sources file')
        self.target.chroot(self.add_java_apt_repo)
        log.info('Creating OMSA sources file')
        sources_path = self.join_root('/etc/apt/sources.list.d/dell-omsa.list')
        source = 'deb %s %s %s\n' % (OMSADebian.mirrorbase, self.dist, self.component)
        deployment.write(sources_path, source)

class OMSARedHat(TargetExtension):
    __configuration__ = {}  # Filled at runtime

    def __init__(self, target_obj):
        self.omsa_bootstrap_url = 'http://mirror.rackspace.com/dell/hardware/dsu/bootstrap.cgi'
        self.proxy = self.__configuration__.get('proxy')
        self.base_omsa_packages = ['srvadmin-all']
        self.gen12_omsa_packages = ['srvadmin-idrac7', 'srvadmin-idracadm7']
        self.gen12_chassis = ['R720', 'R820']
        super(OMSARedHat, self).__init__(target_obj)

    def download_and_prepare_repositories(self):
        log.debug("Configuring Dell System Update repository.")
        wget_command = 'wget -q -O - %s | bash' % (self.omsa_bootstrap_url, )
        if self.proxy:
            wget_command = 'export http_proxy=http://%s HTTPS_PROXY=http://%s ;' % (self.proxy, self.proxy) + wget_command
        self.target.chroot(wget_command)

    def open_manage_packages(self):
        product_name = self.target.get_product_name()
        packages = self.base_omsa_packages
        for chassis in self.gen12_chassis:
            if chassis in product_name:
                packages += self.gen12_omsa_packages
        return packages

    def install_openmanage(self):
        self.target.install_packages(self.open_manage_packages())

    def install_wget(self):
        self.target.install_package('wget')

    def run(self):
        self.target.baseline_yum(self.proxy)
        self.install_wget()
        self.download_and_prepare_repositories()
        self.install_openmanage()
        self.target.revert_yum(self.proxy)


class OMSARHEL7(OMSARedHat):
    __extends__ = 'enterprise_linux_7'

class OMSARHEL6(OMSARedHat):
    __extends__ = 'enterprise_linux_6'

    def install_openmanage(self):
        self.target.install_packages(self.open_manage_packages())
        self.target.service_control('sblim-sfcb', 'stop')