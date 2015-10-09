import logging

from .enterprise_linux_7_target import EL7Target

log = logging.getLogger(__name__)


class CentOS7Target(EL7Target):
    name = 'centos_7'

