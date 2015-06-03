import os
import logging

from press.helpers import deployment
from press.targets.linux.linux_target import LinuxTarget


log = logging.getLogger(__name__)


class RedhatTarget(LinuxTarget):
    name = 'redhat'

    rpm_path = '/usr/bin/rpm'
    yum_path = '/usr/bin/yum'

    def get_package_list(self):
        command = '%s --query --all --queryformat \"%%{NAME}\\n\"' % self.rpm_path
        out = self.chroot(command, quiet=True)
        return out.splitlines()

    def install_package(self, package):
        command = '%s install -y --quiet %s' % (self.yum_path, package)
        res = self.chroot(command)
        if res.returncode:
            log.error('Failed to install package %s' % package)
        log.info('Installed: %s' % package)

    def install_pacakges(self, packages):
        command = '%s installl -y --quiet %s' % (self.yum_path, ' '.join(packages))
        res = self.chroot(command)
        if res.returncode:
            log.error('Failed to install packages: %s' % ' '.join(packages))
        log.info('Installed: %s' % ' '.join(packages))
        return res.returncode

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

    @property
    def has_os_release(self):
        return os.path.exists(self.join_root('/etc/os-release'))

    @property
    def has_redhat_release(self):
        return os.path.exists(self.join_root('/etc/redhat-release'))

    @property
    def os_release(self):
        release_info = dict()
        if not self.has_os_release:
            return release_info
        data = deployment.read(self.join_root('/etc/os-release'))
        for line in data.splitlines():
            line = line.strip()
            if line:
                k, v = line.split('=')
                release_info[k.lower()] = v.strip('\"')
        return release_info

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
            log.error('Error parsing redhat-relase')
        return release_info