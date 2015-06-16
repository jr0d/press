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



