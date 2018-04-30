import logging
import os

from press.exceptions import ServerManagementException
from press.helpers import deployment
from press.targets.target_base import TargetExtension

pgp_key_files = ['hpPublicKey1024.pub',
                 'hpPublicKey2048.pub',
                 'hpPublicKey2048_key1.pub',
                 'hpePublicKey2048_key1.pub']

hp_packages = ['hponcfg', 'ssacli', 'hp-health', 'hp-snmp-agents', 'hp-scripting-tools']

log = logging.getLogger('press.plugins.server_management')


class SPPDebian(TargetExtension):
    dist = ''
    sources_to_add = {'mcp': 'HP Management Component Pack', 'stk': 'HP Proliant Scripting Toolkit'}
    mirrorbase = 'https://mirror.rackspace.com/hp/SDR/repo/{source_name}/'

    def write_sources(self):
        for source_name, source_description in self.sources_to_add.items():
            log.info('Creating {source_description} APT sources file'.format(source_description=source_description))
            sources_path = self.join_root(
                '/etc/apt/sources.list.d/hp-{source_name}.list'.format(source_name=source_name))
            source = '\n'.join([
                '# {source_description}'.format(source_description=source_description),
                'deb {base_url} {dist}/current non-free\n'.format(
                    base_url=self.mirrorbase.format(source_name=source_name),
                    dist=self.dist)
            ])
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
            log.info('Importing HP public key %s' % (pgp_key_file,))
            self.target.chroot('apt-key add %s' % os.path.join(
                self.target.chroot_staging_dir,
                pgp_key_file))

    def install_hp_packages(self):
        self.target.install_packages(hp_packages)

    def run(self):
        self.write_sources()
        self.import_key()
        self.target.apt_update()
        self.install_hp_packages()


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
        self.dmi_product_name = '/sys/class/dmi/id/product_name'
        try:
            self.generation = deployment.read(self.dmi_product_name).split()[-1].lower()
        except IOError:
            raise ServerManagementException(
                '{} is not present. Verify /sys is present and this is an HP chassis'.format(
                    self.dmi_product_name))
        self.hp_repos = {'spp-{generation}'.format(generation=self.generation): 'HP Service Pack for Proliant',
                         'stk': 'HP Proliant Scripting Toolkit'}
        self.repo_file = '/etc/yum.repos.d/hp-{repo_id}.repo'
        self.repo_template = '\n'.join([
            '[hp-{repo_id}]',
            'name = {repo_name}',
            'baseurl = https://mirror.rackspace.com/hp/SDR/repo/{repo_id}/rhel/\$releasever/\$basearch/current',
            'enabled = 1',
            'gpgcheck = 1',
            'gpgkey = https://mirror.rackspace.com/hp/SDR/hpePublicKey2048_key1.pub',
            '         https://mirror.rackspace.com/hp/SDR/hpPublicKey2048_key1.pub',
            'exclude = kmod-elx-lpfc*'
        ])
        self.proxy = self.__configuration__.get('proxy')
        super(SPPRHEL, self).__init__(target_obj)

    def prepare_repositories(self):
        for repo_id, repo_name in self.hp_repos.items():
            log.info("Updating repos to add {repo_name}".format(repo_name=repo_name))
            self.target.chroot('echo "{0}" > "{1}"'.format(
                self.repo_template.format(repo_id=repo_id, repo_name=repo_name),
                self.repo_file.format(repo_id=repo_id)))

    def install_hp_packages(self):
        self.target.install_packages(hp_packages)

    def run(self):
        self.target.baseline_yum(self.proxy)
        self.prepare_repositories()
        self.install_hp_packages()
        self.target.revert_yum(self.proxy)


class SPPRHEL7(SPPRHEL):
    __extends__ = 'enterprise_linux_7'


class SPPRHEL6(SPPRHEL):
    __extends__ = 'enterprise_linux_6'
