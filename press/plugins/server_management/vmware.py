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
        self.rhel_repo_name = 'rhel_base'
        self.proxy = self.__configuration__.get('proxy')
        self.os_id = None

        super(VMWareToolsEL, self).__init__(target_obj)

    def install_vmware_tools(self):
        log.info('Installing vmware tools')
        self.target.install_package('open-vm-tools')

    def run(self):
        self.target.baseline_yum(self.proxy)
        self.install_vmware_tools()
        self.target.revert_yum(self.proxy)

class VMWareToolsEL7(VMWareToolsEL):
    __extends__ = 'enterprise_linux_7'

class VMWareToolsEL6(VMWareToolsEL):
    __extends__ = 'enterprise_linux_6'
