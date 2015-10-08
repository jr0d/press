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
        self.repository_rpm_url = 'http://mirror.rackspace.com/dell/hardware/latest/mirrors.cgi/' \
                                  'osname=rhel{{version}}&basearch=x86_64' \
                                  '&native=1&getrpm=dell-omsa-repository&redirpath='.format(version=self.version)
        super(OMSARedHat, self).__init__(target_obj)

    def download_and_prepare_repositories(self):
        self.target.chroot('try wget -O dell-omsa-repository.rpm "{0}"'.format(self.repository_rpm_url))
        self.target.chroot('echo bootstrapurl=http://mirror.rackspace.com/dell/hardware/latest/bootstrap.cgi'
                           '  > /etc/yum.repos.d/dell-omsa-repository.repo')

    def install_omsa_repo(self):
        self.target.chroot('rpm -i dell-omsa-repository.rpm')

    def install_openmanage(self):
        self.target.install_package('srvadmin-all')

    def run(self):
        self.download_and_prepare_repositories()
        self.install_omsa_repo()
        self.install_openmanage()


class OMSARHEL7(OMSARedHat):
    __extends__ = 'rhel_7'

    def __init__(self, target_obj):
        super(OMSARHEL7, self).__init__(target_obj, version='7')


class OMSACentOS7(OMSARedHat):
    __extends__ = 'centos_7'

    def __init__(self, target_obj):
        super(OMSACentOS7, self).__init__(target_obj, version='7')


