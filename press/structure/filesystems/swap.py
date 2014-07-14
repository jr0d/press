from press.cli import run
from . import FileSystem
from ..exceptions import FileSystemCreateException
import logging

log = logging.getLogger(__name__)


class SWAP(FileSystem):
    fs_type = 'swap'

    def __init__(self, fs_label=None, command_path='/usr/bin/mkswap', mount_options=None):
        super(SWAP, self).__init__(fs_label, mount_options, 0)
        self.command_path = command_path

        self.command = '{command_path} {label_option} {device}'
        self.mount_options = mount_options or self.default_mount_options

        if self.fs_label:
            self.label_option = ' -L %s' % self.fs_label
        else:
            self.label_option = ''

    def create(self, device):
        command = self.command.format(**dict(
            command_path=self.command_path,
            label_option=self.label_option,
            device=device
        ))
        log.info("Creating filesystem: %s" % command)
        result = run(command)

        if result.returncode:
            raise FileSystemCreateException(self.label, command, result)