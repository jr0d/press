import logging

from press.helpers.cli import run
from press.layout.filesystems import FileSystem
from press.exceptions import FileSystemCreateException, FileSystemFindCommandException


log = logging.getLogger(__name__)


class EXT(FileSystem):
    fs_type = ''
    command_name = ''

    # class level defaults
    _default_superuser_reserve = .03
    _default_stride_size = 0
    _default_stripe_width = 0

    def __init__(self, label=None, mount_options=None, **extra):

        super(EXT, self).__init__(label, mount_options)

        self.superuser_reserve = extra.get('super_user_reserve', self._default_superuser_reserve)
        self.stride_size = extra.get('stride_size', self._default_stride_size)
        self.stripe_width = extra.get('stripe_width', self._default_stripe_width)

        self.command_path = self.locate_command(self.command_name)

        if not self.command_path:
            raise \
                FileSystemFindCommandException(
                    'Cannot locate %s in PATH' % self.command_name)

        self.full_command = \
            '{command_path} -U{uuid} -m{superuser_reserve} {extended_options}{label_options} {device}'

        # algorithm for calculating stripe-width: stride * N where N are member disks that are not used
        # as parity disks or hot spares
        self.extended_options = ''
        if self.stripe_width and self.stride_size:
            self.extended_options = ' -E stride=%s,stripe_width=%s' % (self.stride_size, self.stripe_width)

        self.label_options = ''
        if self.fs_label:
            self.label_options = ' -L %s' % self.fs_label

        self.require_fsck = True

    def create(self, device):
        command = self.full_command.format(
            **dict(
                command_path=self.command_path,
                superuser_reserve=self.superuser_reserve,
                extended_options=self.extended_options,
                label_options=self.label_options,
                device=device,
                uuid=self.fs_uuid
            )
        )
        log.info("Creating filesystem: %s" % command)
        result = run(command)

        if result.returncode:
            raise FileSystemCreateException(self.fs_label, command, result)


class EXT2(EXT):
    fs_type = 'ext2'
    command_name = 'mkfs.ext2'


class EXT3(EXT):
    fs_type = 'ext3'
    command_name = 'mkfs.ext3'


class EXT4(EXT):
    fs_type = 'ext4'
    command_name = 'mkfs.ext4'

