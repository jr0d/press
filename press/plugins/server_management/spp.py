import logging
import os

from press.exceptions import ServerManagementException
from press.helpers import deployment
from press.targets.target_base import TargetExtension

pgp_key_files = ['hpPublicKey1024.pub',
                 'hpPublicKey2048.pub',
                 'hpPublicKey2048_key1.pub',
                 'hpePublicKey2048_key1.pub']

spp_packages = ['hponcfg', 'hpssacli', 'hp-health', 'hp-snmp-agents']

log = logging.getLogger('press.plugins.server_management')


class SPPDebian(TargetExtension):
    dist = ''
    mirrorbase = 'http://mirror.rackspace.com/hp/SDR/repo/mcp/'

    def write_sources(self):
        log.info('Creating SPP sources file')
        sources_path = self.join_root('/etc/apt/sources.list.d/hp-spp.list')
        source = 'deb %s %s/current non-free\n' % (SPPDebian.mirrorbase,
                                                   self.dist)
        deployment.write(sources_path, source)

    def import_key(self):
        for pgp_key_file in pgp_key_files:
            key_file_path = os.path.join(os.path.dirname(__file__),
                                         pgp_key_file)
            key_data = deployment.read(key_file_path)
            destination = os.path.join(
                self.join_root(self.target.chroot_staging_dir),
                pgp_key_file)
            deployment.write(destination, key_data)
            log.info('Importing HP public key %s' % (pgp_key_file, ))
            self.target.chroot('apt-key add %s' % os.path.join(
                self.target.chroot_staging_dir,
                pgp_key_file))

    def install_spp(self):
        self.target.install_packages(spp_packages)

    def run(self):
        self.write_sources()
        self.import_key()
        self.target.apt_update()
        self.install_spp()


class SPPDebian8(SPPDebian):
    __extends__ = 'debian_8'
    dist = 'jessie'


class SPPDebian9(SPPDebian):
    __extends__ = 'debian_9'
    dist = 'xenial'


class SPPUbuntu1404(SPPDebian):
    __extends__ = 'ubuntu_1404'
    dist = 'trusty'


class SPPUbuntu1604(SPPDebian):
    __extends__ = 'ubuntu_1604'
    dist = 'xenial'


class SPPRHEL(TargetExtension):
    __configuration__ = {}  # Filled at runtime

    def __init__(self, target_obj):
        self.common_url = 'http://mirror.rackspace.com/hp/SDR'
        self.mirrorbase = '{common_url}/repo/spp/RHEL/{version}/x86_64/current/'
        self.spp_repo_file = '/etc/yum.repos.d/hp-spp.repo'
        self.hpe_gpgkey = '{common_url}/hpePublicKey2048_key1.pub'.format(common_url=self.common_url)
        self.hp_gpgkey = '{common_url}/hpPublicKey2048_key1.pub'.format(common_url=self.common_url)
        self.rhel_repo_name = 'rhel_base'
        self.spp_source = '\n'.join([
            '[spp]',
            'name=HP SPP',
            'baseurl={mirror}'.format(mirror=self.mirrorbase),
            'enabled=1',
            'gpgcheck=1',
            'gpgkey={gpgkey_1}\n       {gpgkey_2}'.format(
                gpgkey_1=self.hpe_gpgkey,
                gpgkey_2=self.hp_gpgkey)
        ])
        self.proxy = self.__configuration__.get('proxy')
        self.os_id = None
        self.dmi_product_name = '/sys/class/dmi/id/product_name'
        try:
            self.generation = deployment.read(self.dmi_product_name).split()[-1].lower()
        except IOError:
            raise ServerManagementException(
                '{} is not present. Verify /sys is present and this is an HP chassis'.format(
                    self.dmi_product_name))
        super(SPPRHEL, self).__init__(target_obj)

    def prepare_repositories(self):
        log.debug("Updating repos to add HP-SPP")
        major_version = self.target.get_el_release_value('major_version')
        self.target.chroot('echo "{0}" > "{1}"'.format(
            self.spp_source.format(common_url=self.common_url, version=major_version), self.spp_repo_file))

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
