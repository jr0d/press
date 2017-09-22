import logging

from press.helpers.cli import run
from press.layout.filesystems import FileSystem
from press.exceptions import (
    FileSystemCreateException,
    FileSystemFindCommandException
)

log = logging.getLogger(__name__)


class XFS(FileSystem):
    fs_type = 'xfs'
    command_name = 'mkfs.xfs'

    xfs_required_mount_options = ['inode64', 'nobarrier']

    def __init__(self, label=None, mount_options=None, **extra):
        super(XFS, self).__init__(label, mount_options)
        self.extra = extra
        for option in self.xfs_required_mount_options:
            if option not in self.mount_options:
                self.mount_options.append(option)

        self.command_path = self.locate_command(self.command_name)

        if not self.command_path:
            raise \
                FileSystemFindCommandException(
                    'Cannot locate %s in PATH' % self.command_name
                )

        self.full_command = \
            '{command_path} -m uuid={uuid} -f {label_options}{device}'

        self.label_options = ''
        if self.fs_label:
            self.label_options = ' -L %s ' % self.fs_label

    def create(self, device):
        command = self.full_command.format(
            **dict(
                command_path=self.command_path,
                uuid=self.fs_uuid,
                label_options=self.label_options,
                device=device
            )
        )
        log.info("Creating filesystem: %s" % command)
        result = run(command)
        if result.returncode:
            raise FileSystemCreateException(self.fs_label, command, result)
