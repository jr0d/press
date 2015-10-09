from press.targets.linux.redhat.enterprise_linux.enterprise_linux_7.enterprise_linux_7_target \
    import EL7Target

from press.targets.linux.redhat.enterprise_linux.enterprise_linux_7.centos_7 import CentOS7Target

target_mapping = {
    'rhel7': EL7Target,
    'centos7': CentOS7Target
}