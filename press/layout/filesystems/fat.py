#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging

from press.helpers.cli import run
from press.layout.filesystems import FileSystem
from press.exceptions import FileSystemCreateException, \
    FileSystemFindCommandException


log = logging.getLogger(__name__)


class FAT32(FileSystem):
    fs_type = 'fat'
    command_name = 'mkfs.fat'

    def __init__(self, label=None, mount_options=None, **extra):
        super(FAT32, self).__init__(label, mount_options, **extra)
        self.extra = extra

        self.command_path = self.locate_command(self.command_name)

        if not self.command_path:
            raise FileSystemFindCommandException(
                'Cannot locate {} in PATH'.format(self.command_name))

        self.full_command = '{command_path} -f {label_options}{device}'

        self.label_options = ''
        if self.fs_label:
            self.label_options = ' -L {} '.format(self.fs_label)

    def create(self, device):
        command = self.full_command.format(
                command_path=self.command_path,
                label_options=self.label_options,
                device=device)

        log.info('Creating filesystem: {}'.format(command))
        result = run(command)
        if result.returncode:
            raise FileSystemCreateException(self.fs_label, command, result)


class EFI(FAT32):
    fs_type = 'efi'

    def __init__(self, label=None, mount_options=None, **extra):
        super(EFI, self).__init__(label, mount_options, **extra)
        self.full_command = '{command_path} -F 32 -f {label_options}{device}'
