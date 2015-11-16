import os
import logging

from press.helpers import deployment
from press.targets.linux.linux_target import LinuxTarget
from press.hooks.hooks import add_hook

log = logging.getLogger(__name__)


class RedhatTarget(LinuxTarget):
    name = 'redhat'

    rpm_path = '/usr/bin/rpm'
    yum_path = '/usr/bin/yum'

    def __init__(self, press_configuration, disks, root, chroot_staging_dir):
        super(RedhatTarget, self).__init__(press_configuration, disks, root, chroot_staging_dir)
        add_hook(self.add_repos, "pre-extensions", self)

    def get_package_list(self):
        command = '%s --query --all --queryformat \"%%{NAME}\\n\"' % self.rpm_path
        out = self.chroot(command, quiet=True)
        return out.splitlines()

    def install_package(self, package):
        command = '%s install -y --quiet %s' % (self.yum_path, package)
        res = self.chroot(command)
        if res.returncode:
            log.error('Failed to install package %s' % package)
        else:
            log.info('Installed: %s' % package)

    def install_packages(self, packages):
        command = '%s install -y --quiet %s' % (self.yum_path, ' '.join(packages))
        res = self.chroot(command)
        if res.returncode:
            log.error('Failed to install packages: %s' % ' '.join(packages))
        else:
            log.info('Installed: %s' % ' '.join(packages))
        return res.returncode

    def add_repo(self, name, mirror, gpgkey):
        path_name = name.lower().replace(" ", "_")
        log.info('Creating repo file for "{name}"'.format(name=name))
        sources_path = self.join_root('/etc/yum.repos.d/{name}.repo'.format(name=path_name))
        source = "[{lower_name}]\nname={formal_name}\nbaseurl={mirror}\nenabled=1".format(lower_name=path_name,
                                                                                          formal_name=name,
                                                                                          mirror=mirror)
        if gpgkey:
            source += "\ngpgcheck=1"
            source += "\ngpgkey={gpgkey}".format(gpgkey=gpgkey)
        else:
            source += "\ngpgcheck=0"

        deployment.write(sources_path, source)

    def add_repos(self, press_config):
        for repo in press_config.get('repos', []):
            self.add_repo(repo['name'], repo['mirror'], repo.get('gpgkey', None))

    def package_exists(self, package_name):
        for package in self.get_package_list():
            if package_name == package.strip():
                return True
        return False

    def packages_exist(self, package_names):
        match = dict([(name, False) for name in package_names])
        for package in self.get_package_list():
            if package in match:
                match[package] = True
        if False in match.values():
            return False
        return True

    def packages_missing(self, packages):
        missing = list()
        installed_packages = self.get_package_list()
        for package in packages:
            if package not in installed_packages:
                missing.append(package)
        return missing

    @property
    def has_redhat_release(self):
        return os.path.exists(self.join_root('/etc/redhat-release'))

    def parse_redhat_release(self):
        """
        Heuristic garbage
        :return:
        """
        release_info = dict()
        if not self.has_redhat_release:
            return release_info
        data = deployment.read(self.join_root('/etc/redhat-release'))
        data = data.strip()
        try:
            release_info['codename'] = data[-1].strip('()')
            release_info['version'] = data[-2]
            release_info['os'] = data.split('release')[0].strip()
        except IndexError:
            log.error('Error parsing redhat-release')
        return release_info

