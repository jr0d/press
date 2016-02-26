import logging
import os
from press.helpers import deployment
from press.targets.target_base import TargetExtension
from press.plugins.server_management.server_management import get_product_name

pgp_key_file = 'dell_key.1285491434D8786F'

log = logging.getLogger('press.plugins.server_management')


class OMSADebian(TargetExtension):
    dist = ''
    mirrorbase = 'http://mirror.rackspace.com/dell/community/ubuntu'

    def write_sources(self):
        log.info('Creating OMSA sources file')
        sources_path = self.join_root('/etc/apt/sources.list.d/dell-omsa.list')
        source = 'deb %s %s openmanage\n' % (OMSADebian.mirrorbase, self.dist)
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


class OMSARedHat(TargetExtension):
    __configuration__ = {}  # Filled at runtime

    def __init__(self, target_obj, omsa_version = 7):
        self.omsa_rpm_url = 'http://mirror.rackspace.com/dell/hardware/latest/mirrors.cgi/' \
                            'osname=rhel{version}&basearch=x86_64' \
                            '&native=1&getrpm=dell-omsa-repository&redirpath='.format(version=omsa_version)
        self.omsa_repo_file = '/etc/yum.repos.d/dell-omsa-repository.repo'
        self.omsa_bootstrap_url = 'http://mirror.rackspace.com/dell/hardware/latest/bootstrap.cgi'
        self.rhel_repo_name = 'rhel_base'
        self.proxy = self.__configuration__.get('proxy')
        self.os_id = None
        self.base_omsa_packages = ['srvadmin-all']
        self.gen12_omsa_packages = ['srvadmin-idrac7', 'srvadmin-idracadm7']
        self.product_name = get_product_name()
        super(OMSARedHat, self).__init__(target_obj)

    def download_and_prepare_repositories(self):
        log.debug("Updating repos to add OMSA")
        wget_command = 'wget -O dell-omsa-repository.rpm "{0}"'.format(self.omsa_rpm_url)
        if self.proxy:
            wget_command = 'http_proxy=http://%s HTTPS_PROXY=http://%s ' % (self.proxy, self.proxy) + wget_command
        self.target.chroot(wget_command)
        self.target.chroot('echo bootstrapurl="{0}" > "{1}"'.format(self.omsa_bootstrap_url, self.omsa_repo_file))

    def install_omsa_repo(self):
        rpm_command = 'rpm -i dell-omsa-repository.rpm'
        if self.proxy:
            rpm_command = 'http_proxy=http://%s HTTPS_PROXY=http://%s ' % (self.proxy, self.proxy) + rpm_command
        self.target.chroot(rpm_command)

    def install_openmanage(self):
        packages = self.base_omsa_packages
        if 'R720' or '820' in self.product_name
            packages += self.gen12_omsa_packages
        self.target.install_packages(packages)

    def install_wget(self):
        self.target.install_package('wget')

    def baseline_yum(self, os_id, rhel_repo_name, version, proxy):
        """
        Check to see if we need proxy, and enable in yum.conf
        Check if we are 'rhel' and if so add base repo
        """
        rhel_repo_url = 'http://intra.mirror.rackspace.com/kickstart/'\
                            'rhel-x86_64-server-{version}.eus/'.format(version=version)
        if proxy:
            self.target.enable_yum_proxy(proxy)
        if os_id == 'rhel':
            self.target.add_repo(rhel_repo_name, rhel_repo_url, gpgkey=None)

    def revert_yum(self, os_id, rhel_repo_name, proxy):
        """
        Reverts changes from baseline yum:
        Disabled proxy
        If 'rhel' removes the base repo
        """
        if proxy:
            self.target.disable_yum_proxy()
        if os_id == 'rhel':
            self.target.remove_repo(rhel_repo_name)

    def run(self):
        self.os_id = self.target.get_os_release_value('ID')
        self.version = self.target.get_os_release_value('VERSION_ID')
        self.baseline_yum(self.os_id, self.rhel_repo_name, self.version, self.proxy)
        self.install_wget()
        self.download_and_prepare_repositories()
        self.install_omsa_repo()
        self.install_openmanage()
        self.revert_yum(self.os_id, self.rhel_repo_name, self.proxy)


class OMSARHEL7(OMSARedHat):
    __extends__ = 'enterprise_linux_7'
