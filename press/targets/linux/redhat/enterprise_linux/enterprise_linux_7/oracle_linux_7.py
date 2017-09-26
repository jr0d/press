import logging

from press.targets.linux.redhat.enterprise_linux.enterprise_linux_7.enterprise_linux_7_target \
    import EL7Target

log = logging.getLogger(__name__)


class Oracle7Target(EL7Target):
    name = 'oracle_linux_7'
    release_file = '/etc/oracle-release'
