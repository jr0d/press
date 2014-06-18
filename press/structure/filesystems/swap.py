from press.cli import run
from . import FileSystem
from ..exceptions import FileSystemCreateException


class SWAP(FileSystem):
    def __init__(self, label=None, command_path='/usr/bin/mkswap'):
        self.label = label
        self.command_path = command_path

        self.command = '{command_path} {label_option} {device}'

        if self.label:
            self.label_option = ' -L %s' % self.label
        else:
            self.label_option = ''

    def create(self, device):
        command = self.command.format(**dict(
            command_path=self.command_path,
            label_option=self.label_option,
            device=device
        ))
        result = run(command)

        if result.returncode:
            raise FileSystemCreateException(self.label, command, result)