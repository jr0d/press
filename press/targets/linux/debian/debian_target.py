import logging

from press.targets.linux.linux_target import LinuxTarget

log = logging.getLogger(__name__)


class DebianTarget(LinuxTarget):
    name = 'debian'

    __apt_command = 'DEBIAN_FRONTEND=noninteractive apt-get -y -qq'

    __query_packages = 'dpkg --get-selections | awk \'{print $1}\''

    def get_package_list(self):
        out = self.chroot(self.__query_packages, quit=True)
        return map(lambda s: s.strip(), out.splitlines())

    def install_package(self, package):
        self.install_packages([package])

    def install_packages(self, packages):
        packages_str = ' '.join(packages)
        log.info('Installing: %s' % packages_str)
        command = self.__apt_command + ' install %s' % packages_str
        res = self.chroot(command)
        if res.returncode:
            log.error('Failed to install packages')
        else:
            log.debug('Installed packages %s' % packages_str)

    def packages_missing(self, packages):
        missing = list()
        installed_packages = self.get_package_list()
        for package in packages:
            if package not in installed_packages:
                missing = package
        return missing

    def remove_package(self, package):
        self.remove_packages([package])

    def remove_packages(self, packages):
        log.info('Removing: %s' % ' '.join(packages))
        self.chroot(self.__apt_command + ' remove %s' % ' '.join(packages))
