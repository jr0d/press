import logging
import os
from press.helpers import deployment
from press.targets.target_base import TargetExtension

pgp_key_files = ['hpPublicKey1024.pub', 'hpPublicKey2048.pub', 'hpPublicKey2048_key1.pub']

spp_packages = ['hponcfg', 'hpssacli', 'hp-health']

log = logging.getLogger('press.plugins.server_management')

class SPPDebian(TargetExtension):
    dist = ''
    mirrorbase = 'http://mirror.rackspace.com/hp/SDR/repo/mcp/'

    def write_sources(self):
        log.info('Creating SPP sources file')
        sources_path = self.join_root('/etc/apt/sources.list.d/hp-spp.list')
        source = 'deb %s %s/current non-free\n' % (SPPDebian.mirrorbase, self.dist)
        deployment.write(sources_path, source)

    def import_key(self):
        for pgp_key_file in pgp_key_files:
            key_file_path = os.path.join(os.path.dirname(__file__), pgp_key_file)
            key_data = deployment.read(key_file_path)
            destination = os.path.join(self.join_root(self.target.chroot_staging_dir),
                                       pgp_key_file)
            deployment.write(destination, key_data)
            log.info('Importing HP public key %s' % (pgp_key_file, ))
            self.target.chroot('apt-key add %s' % os.path.join(self.target.chroot_staging_dir,
                                                           pgp_key_file))

    def install_spp(self):
        self.target.install_packages(spp_packages)

    def run(self):
        self.write_sources()
        self.import_key()
        self.target.apt_update()
        self.install_spp()


class SPPUbuntu1404(SPPDebian):
    __extends__ = 'ubuntu_1404'
    dist = 'trusty'



