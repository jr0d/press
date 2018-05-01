import logging
import os
from press.helpers import deployment
from press.targets.target_base import TargetExtension

pgp_key_file = 'dell_key.1285491434D8786F'

log = logging.getLogger('press.plugins.server_management')


class OMSADebian(TargetExtension):
    dist = ''
    mirrorbase = 'https://mirror.rackspace.com/dell/community/ubuntu'
    component = 'openmanage'

    def write_sources(self):
        log.info('Creating OMSA sources file')
        sources_path = self.join_root('/etc/apt/sources.list.d/dell-omsa.list')
        source = 'deb {} {} {}\n'.format(OMSADebian.mirrorbase,
                                         self.dist,
                                         self.component)
        deployment.write(sources_path, source)

    def import_key(self):
        key_file_path = os.path.join(os.path.dirname(__file__), pgp_key_file)
        key_data = deployment.read(key_file_path)
        destination = os.path.join(self.join_root(
            self.target.chroot_staging_dir), pgp_key_file)
        deployment.write(destination, key_data)
        log.info('Importing Dell public key')
        self.target.chroot('apt-key add {}'.format(
            os.path.join(self.target.chroot_staging_dir, pgp_key_file)))

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


class OMSADebian8(OMSADebian):
    __extends__ = 'debian_8'
    dist = 'jessie'


class OMSAUbuntu1404(OMSADebian):
    __extends__ = 'ubuntu_1404'
    dist = 'trusty'


class OMSAUbuntu1604(OMSADebian):
    __extends__ = 'ubuntu_1604'
    dist = 'xenial'


class OMSARedHat(TargetExtension):
    __configuration__ = {}  # Filled at runtime

    def __init__(self, target_obj):
        self.omsa_bootstrap_url = \
            'https://mirror.rackspace.com/dell/hardware/dsu/bootstrap.cgi'
        self.proxy = self.__configuration__.get('proxy')
        self.base_omsa_packages = ['srvadmin-all']
        self.gen12_omsa_packages = ['srvadmin-idrac7', 'srvadmin-idracadm7']
        self.gen12_chassis = ['R720', 'R820']
        # Dell R740/14G work around
        self.dell_repos = 'dell-system-update_dependent ' \
                          'dell-system-update_independent'
        self.gen14_chassis = 'R740'
        self.gen14_gpg_key = \
            'https://linux.dell.com/repo/hardware/dsu/public.key'
        # TODO Will need to modify URL in OMSARHEL6() class if/when EL6 verison is available
        self.gen14_tmp_repo_url = 'https://mirror.rackspace.com/omsa91/EL7/'
        self.gen14_tmp_boorstrap_url = \
            'https://linux.dell.com/repo/hardware/dsu/bootstrap.cgi'
        self.gen14_tmp_repo_name = 'omsa91'

        super(OMSARedHat, self).__init__(target_obj)
        self.product_name = self.target.get_product_name()
        self.is_gen14 = self.gen14_chassis in self.product_name

    def download_and_prepare_repositories(self, url):
        log.debug("Configuring Dell System Update repository.")
        wget_command = 'wget -q -O - {} | bash'.format(url)
        if self.proxy:
            wget_command = 'export http_proxy=http://{0} ' \
                           'https_proxy=http://{0} ; {1}'.format(self.proxy,
                                                                 wget_command)
        self.target.chroot(wget_command)

    def open_manage_packages(self):
        packages = self.base_omsa_packages
        for chassis in self.gen12_chassis:
            if chassis in self.product_name:
                packages += self.gen12_omsa_packages
        return packages

    def tmp_gen14_fix(self):
        self.target.chroot('yum-config-manager --disable ' + self.dell_repos)
        self.target.add_repo(self.gen14_tmp_repo_name, self.gen14_tmp_repo_url,
                             self.gen14_gpg_key)

    def tmp_gen14_clean(self):
        self.target.chroot('yum-config-manager --enable ' + self.dell_repos)
        self.target.remove_repo(self.gen14_tmp_repo_name)

    def install_openmanage(self):
        self.target.install_packages(self.open_manage_packages())

    def install_wget(self):
        self.target.install_package('wget')

    def run(self):
        self.target.baseline_yum(self.proxy)
        self.install_wget()
        self.download_and_prepare_repositories(self.omsa_bootstrap_url)
        if self.is_gen14:
            self.tmp_gen14_fix()
        self.install_openmanage()
        if self.is_gen14:
            self.tmp_gen14_clean()
        self.target.revert_yum(self.proxy)


class OMSARHEL7(OMSARedHat):
    __extends__ = 'enterprise_linux_7'


class OMSARHEL6(OMSARedHat):
    __extends__ = 'enterprise_linux_6'

    def install_openmanage(self):
        self.target.install_packages(self.open_manage_packages())
        self.target.service_control('sblim-sfcb', 'stop')
        self.target.service_control('dataeng', 'stop')

    # Temp fix for EL6 kicks with 14G servers, once RAX mirrors are synced
    # will revert back changes
    def tmp_gen14_fix(self):
        url = self.gen14_tmp_boorstrap_url
        self.download_and_prepare_repositories(url)

    def tmp_gen14_clean(self):
        pass
