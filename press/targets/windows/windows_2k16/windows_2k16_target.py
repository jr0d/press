import logging

from press.targets.windows.windows_target import WindowsTarget

log = logging.getLogger(__name__)


class Win2k16Target(WindowsTarget):
    name = 'windows_2k16'
