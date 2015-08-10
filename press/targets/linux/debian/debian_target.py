import logging

from press.helpers import deployment
from press.targets.linux.linux_target import LinuxTarget
from press.targets.linux.debian.networking import debian_networking

log = logging.getLogger(__name__)



class DebianTarget(LinuxTarget):
    name = 'debian'

    __apt_command = 'DEBIAN_FRONTEND=noninteractive apt-get -y'

    __query_packages = 'dpkg --get-selections | awk \'{print $1}\''
    __reconfigure_package = 'dpkg-reconfigure --frontend noninteractive '
    __start_hack_script = '#!/bin/sh\nexit 101\n'
    __start_hack_path = '/usr/sbin/policy-rc.d'

    def __init__(self, press_configuration, disks, root, chroot_staging_dir):
        super(DebianTarget, self).__init__(press_configuration,
                                           disks, root, chroot_staging_dir)
        self.cache_updated = False

    def insert_no_start_hack(self):
        log.info('Inserting NOSTART hack')
        deployment.write(self.join_root(self.__start_hack_path),
                         self.__start_hack_script, mode=0755)

    def remove_no_start_hack(self):
        log.info('Removing NOSTART hack')
        deployment.remove_file(self.join_root(self.__start_hack_path))

    def get_package_list(self):
        out = self.chroot(self.__query_packages, quiet=True)
        return map(lambda s: s.strip(), out.splitlines())

    def apt_update(self):
        res = self.chroot(self.__apt_command + ' update', proxy=self.proxy)
        if res.returncode:
            log.error('Failed to update apt-cache')
        else:
            self.cache_updated = True

    def install_package(self, package):
        self.install_packages([package])

    def install_packages(self, packages):
        if not self.cache_updated:
            self.apt_update()
        packages_str = ' '.join(packages)
        command = self.__apt_command + ' install %s' % packages_str
        self.insert_no_start_hack()
        log.info('Installing packages: %s' % packages_str)
        res = self.chroot(command, proxy=self.proxy)
        self.remove_no_start_hack()
        if res.returncode:
            log.error('Failed to install packages')
        else:
            log.debug('Installed packages %s' % packages_str)

    def packages_missing(self, packages):
        missing = list()
        installed_packages = self.get_package_list()
        for package in packages:
            if package not in installed_packages:
                missing.append(package)
        return missing

    def remove_package(self, package):
        self.remove_packages([package])

    def remove_packages(self, packages):
        log.info('Removing packages: %s' % ' '.join(packages))
        self.chroot(self.__apt_command + ' remove --purge %s' % ' '.join(packages))

    def reconfigure_package(self, package):
        log.info('Reconfiguring package: %s' % package)
        self.chroot(self.__reconfigure_package + package)

    def set_timezone(self, timezone):
        localtime_path = '/etc/localtime'
        deployment.remove_file(self.join_root(localtime_path))
        deployment.write(self.join_root(localtime_path), timezone)
        self.reconfigure_package('tzdata')

    def write_interfaces(self):
        interfaces_path = self.join_root('/etc/network/interfaces')
        if self.network_configuration:
            log.info('Writing network configuration')
            debian_networking.write_interfaces(interfaces_path, self.network_configuration)

    def localization(self):
        configuration = self.press_configuration.get('localization', dict())

        language = configuration.get('language')
        if language:
            log.info('Setting LANG=%s' % language)
            self.set_language(language)

        timezone = configuration.get('timezone')
        if timezone:
            log.info('Setting localtime: %s' % timezone)
            self.set_timezone(timezone)

        ntp_server = configuration.get('ntp_server')
        if ntp_server:
            log.info('Syncing time with: %s' % ntp_server)
            self.set_time(ntp_server)

