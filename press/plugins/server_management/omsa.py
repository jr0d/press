import logging
import os
from press.helpers import deployment
from press.targets.target_base import TargetExtension

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

    def __init__(self, target_obj, version='7'):
        self.version = version
        self.omsa_rpm_url = 'http://mirror.rackspace.com/dell/hardware/latest/mirrors.cgi/' \
                                  'osname=rhel{version}&basearch=x86_64' \
                                  '&native=1&getrpm=dell-omsa-repository&redirpath='.format(version=self.version)
        self.omsa_repo_file = '/etc/yum.repos.d/dell-omsa-repository.repo'
        self.omsa_bootstrap_url = 'http://mirror.rackspace.com/dell/hardware/latest/bootstrap.cgi'
        self.rhel_repo_name = 'rhel_base'
        self.proxy = self.target.press_configuration.get('proxy')
        self.os_release = self.target.parse_os_release()
        self.os_id = self.os_release.get('ID')
        super(OMSARedHat, self).__init__(target_obj)

    def download_and_prepare_repositories(self):
        log.debug("Updating repos to add OMSA")
        self.target.chroot('wget -O dell-omsa-repository.rpm "{0}"'.format(self.omsa_rpm_url))
        self.target.chroot('echo bootstrapurl="{0}" > "{1}"'.format(self.omsa_bootstrap_url, self.omsa_repo_file))

    def install_omsa_repo(self):
        self.target.chroot('rpm -i dell-omsa-repository.rpm')

    def install_openmanage(self):
        self.target.install_package('srvadmin-all')

    def install_wget(self):
        self.target.install_package('wget')

    def normalize_yum(self):
        self.target.disable_proxy(self.proxy)
        if self.os_id == 'rhel':
            self.target.remove_repo(self.rhel_repo_name)

    def run(self):
        self.target.baseline_yum(self.os_id, self.rhel_repo_name, self.version, self.proxy)
        self.install_wget()
        self.download_and_prepare_repositories()
        self.install_omsa_repo()
        self.install_openmanage()
        self.target.revert_yum(self.os_id, self.rhel_repo_name)


class OMSARHEL7(OMSARedHat):
    __extends__ = 'enterprise_linux_7'
