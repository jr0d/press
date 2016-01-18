import logging
import os
from press.helpers import deployment
from press.targets.target_base import TargetExtension

log = logging.getLogger('press.plugins.server_management')


class VMWareTools(TargetExtension):
    __extends__ = 'ubuntu_1404'

    def run(self):
        log.info('Install vmware tools')
        self.target.install_packages(['open-vm-tools', 'open-vm-dkms'])

class VMWareToolsEL(TargetExtension):
    __configuration__ = {}

    def __init__(self, target_obj):
        self.version = self.target.get_os_release_value('VERSION_ID')
        self.rhel_repo_name = 'rhel_base'
        self.proxy = self.__configuration__.get('proxy')
        self.os_id = None

        super(VMWareToolsEL, self).__init__(target_obj)

    def install_vmware_tools(self):
        log.info('Installing vmware tools')
        self.target.install_package('open-vm-tools')

    def baseline_yum(self, os_id, rhel_repo_name, version, proxy):
        """
        Check to see if we need proxy, and enable in yum.conf
        Check if we are 'rhel' and if so add base repo
        """
        rhel_repo_url = 'http://intra.mirror.rackspace.com/kickstart/'\
                            'rhel-x86_64-server-{version}.eus/'.format(version=version)
        if proxy:
            self.target.enable_yum_proxy(proxy)
        if os_id == 'rhel':
            self.target.add_repo(rhel_repo_name, rhel_repo_url, gpgkey=None)

    def revert_yum(self, os_id, rhel_repo_name, proxy):
        """
        Reverts changes from baseline yum:
        Disabled proxy
        If 'rhel' removes the base repo
        """
        if proxy:
            self.target.disable_yum_proxy()
        if os_id == 'rhel':
            self.target.remove_repo(rhel_repo_name)


    def run(self):
        self.os_id = self.target.get_os_release_value('ID')
        self.baseline_yum(self.os_id, self.rhel_repo_name, self.version, self.proxy)
        self.install_vmware_tools()
        self.revert_yum(self.os_id, self.rhel_repo_name, self.proxy)

class VMWareToolsEL7(VMWareToolsEL):
    __extends__ = 'enterprise_linux_7'
