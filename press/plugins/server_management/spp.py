import logging
import os
from press.helpers import deployment
from press.targets.target_base import TargetExtension


pgp_key_files = ['hpPublicKey1024.pub', 'hpPublicKey2048.pub', 'hpPublicKey2048_key1.pub']

spp_packages = ['hponcfg', 'hpssacli', 'hp-health', 'hp-snmp-agents']

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

class SPPUbuntu1604(SPPDebian):
    __extends__ = 'ubuntu_1604'
    dist = 'xenial'

class SPPRHEL(TargetExtension):
    __configuration__ = {} # Filled at runtime

    def __init__(self, target_obj):
        self.mirrorbase = 'http://mirror.rackspace.com/hp/SDR/repo/spp' \
                          '/RHEL/{version}/x86_64/current/'
        self.spp_repo_file = '/etc/yum.repos.d/hp-spp.repo'
        self.gpgkey = 'http://mirror.rackspace.com/hp/SDR/repo/spp/GPG-KEY-SPP'
        self.rhel_repo_name = 'rhel_base'
        self.spp_source = '[spp]\nname=HP SPP\nbaseurl={mirror}\nenabled=1' \
                          '\ngpgcheck=1\ngpgkey={gpgkey}'.format(mirror=self.mirrorbase, gpgkey=self.gpgkey)
        self.proxy = self.__configuration__.get('proxy')
        self.os_id = None

        super(SPPRHEL, self).__init__(target_obj)

    def prepare_repositories(self):
        log.debug("Updating repos to add HP-SPP")
        short_version  = self.target.get_redhat_release_value('short_version')
        self.target.chroot('echo "{0}" > "{1}"'.format(self.spp_source.format(version=short_version), self.spp_repo_file))

    def install_hp_spp(self):
        self.target.install_packages(spp_packages)

    def run(self):
        self.target.baseline_yum(self.proxy)
        self.prepare_repositories()
        self.install_hp_spp()
        self.target.revert_yum(self.proxy)

class SPPRHEL7(SPPRHEL):
    __extends__ = 'enterprise_linux_7'


class SPPRHEL6(SPPRHEL):
    __extends__ = 'enterprise_linux_6'

