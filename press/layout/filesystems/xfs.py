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
    xfs_admin = 'xfs_admin'

    xfs_required_mount_options = ['inode64', 'nobarrier']

    def __init__(self, label=None, mount_options=None, **extra):
        super(XFS, self).__init__(label, mount_options)
        self.extra = extra
        for option in self.xfs_required_mount_options:
            if option not in self.mount_options:
                self.mount_options.append(option)

        self.command_path = self.locate_command(self.command_name)
        self.xfs_admin_path = self.locate_command(self.xfs_admin)

        if not self.command_path:
            raise \
                FileSystemFindCommandException(
                    'Cannot locate %s in PATH' % self.command_name
                )

        if not self.xfs_admin_path:
            raise \
                FileSystemFindCommandException(
                    'Cannot locate %s in PATH' % self.xfs_admin_path
                )

        self.full_command = \
            '{command_path} -f {label_options}{device}'

        self.label_options = ''
        if self.fs_label:
            self.label_options = ' -L %s ' % self.fs_label

        self.xfs_admin_command = '{command_path} -U {uuid} {device}'

    def create(self, device):
        command = self.full_command.format(
            **dict(
                command_path=self.command_path,
                label_options=self.label_options,
                device=device
            )
        )
        log.info("Creating filesystem: %s" % command)
        result = run(command)
        if result.returncode:
            raise FileSystemCreateException(self.fs_label, command, result)

        command = self.xfs_admin_command.format(**dict(command_path=self.xfs_admin_path,
                                                       uuid=self.fs_uuid,
                                                       device=device))
        log.info('Setting UUID: %s' % self.fs_uuid)

        result = run(command)
        if result.returncode:
            raise FileSystemCreateException(self.fs_label, command, result)
