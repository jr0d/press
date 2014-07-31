"""
Original Author: Jeff Ness
"""

import logging
import subprocess

from press.structure.size import Size

log = logging.getLogger(__name__)


class LVMError(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class LVM(object):
    """
    Class to interacting with LVM in Python.
    """

    pvdisplay_command = 'pvdisplay -C --separator : --unit b -o +pvseg_size'
    vgdisplay_command = 'vgdisplay -C --separator : --unit b -o +vg_all'

    def __init__(self):
        """
        LVM Class constructor.
        """
        # List of required system binaries
        self.binaries = [
            'pvcreate', 'pvremove', 'pvdisplay',
            'vgcreate', 'vgremove', 'vgdisplay',
            'lvcreate', 'lvremove', 'lvdisplay',
            'vgchange'
        ]

        self.__verify_binaries(self.binaries)

    def __verify_binaries(self, binaries):
        """
        Make sure all binaries are on system.
        """
        for binary in binaries:
            check = self.__execute('which %s' % binary)
            if not check[0]:
                raise LVMError('Missing required binary "%s"' % binary)

    @staticmethod
    def __execute(command):
        """
        Execute a shell command using subprocess, then validate the return
        code and log either stdout or stderror to the logger.
        """
        log.debug('Running: %s' % command)
        process = subprocess.Popen(command,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return_code = process.wait()
        response = process.communicate()

        if return_code > 0:
            log.error('stderr: %s' % response[1])
            raise LVMError('Return code: %s' % return_code)

        return response[0]

    @staticmethod
    def __to_dict(stdout):
        """
        Takes output from lvm commands and converts to dict
        """
        stdout = stdout.splitlines()
        stdout = filter(None, stdout)
        headers = stdout.pop(0)
        headers = headers.strip().split(':')

        response = []
        for line in stdout:
            values = line.strip().split(':')
            response.append(dict(zip(headers, values)))

        return response

    def pvcreate(self, physical_volume):
        """
        Create a physical volume using pvcreate command line tool.
        """
        log.info('running pvcreate')
        command = 'pvcreate %s' % physical_volume
        return self.__execute(command)

    def pvremove(self, physical_volume):
        """
        Delete a physical volume using pvcreate command line tool.
        """
        log.info('running pvremove')
        command = 'pvremove %s' % physical_volume
        return self.__execute(command)

    def pvdisplay(self, physical_volume=''):
        """
        Display a physical volume using pvdisplay command line tool.
        """
        log.info('running pvdisplay')
        command = '%s %s' % (self.pvdisplay_command, physical_volume)
        res = self.__execute(command)
        return self.__to_dict(res)

    def vgcreate(self, group_label, physical_volumes):
        """
        Create a volume group using vgcreate command line tool.

        physical_volumes is a list containing at least one physical_volume,
        or a single physical_volume.
        """
        # If input physical_volumes was a list lets create space seperated,
        # list of pvs
        log.info('running vgcreate')
        if type(physical_volumes) == list:
            physical_volumes = ' '.join(physical_volumes)

        command = 'vgcreate %s %s' % (group_label, physical_volumes)
        return self.__execute(command)

    def vgremove(self, group_label):
        """
        Delete a volume group by label using vgremove command line tool.
        """
        log.info('running vgremove')
        command = 'vgremove -f %s' % group_label
        return self.__execute(command)

    def vgdisplay(self, group_label=''):
        """
        Display a volume group using vgdisplay command line tool.
        """
        log.info('running vgdisplay')
        command = 'vgdisplay -C --separator : --unit b %s' % group_label
        res = self.__execute(command)
        return self.__to_dict(res)

    def lvcreate(self, size, group_label, volume_label):
        """
        Create a logical volume using lvcreate command line tool.

        Size should be a size with appended size type, for example:
        100MB would represent 100 Megabytes, while 2GB would represent
        2 Gigabytes.
        """
        log.info('running lvcreate')
        command = 'lvcreate -L %s -n %s %s' % (size, volume_label, group_label)
        return self.__execute(command)

    def lvdisplay(self, combined_label=''):
        """
        Display a logical volume using lvdisplay command line tool.
        """
        log.info('running lvdisplay')
        command = 'lvdisplay -C --separator : --unit b %s' % combined_label
        res = self.__execute(command)
        return self.__to_dict(res)

    def lvremove(self, combined_label):
        """
        Deletes a logical volume using lvremove command line tool.get_logger
        """
        log.info('running lvremove')
        command = 'lvremove -f %s' % combined_label
        return self.__execute(command)

    def vgchange(self, args):
        command = 'vgchange %s' % args
        return self.__execute(command)

    def activate_volume(self, volume_group):
        return self.vgchange('-a y %s' % volume_group)

    def get_pe_size(self, physical_volume):
        data = self.pvdisplay(physical_volume)
        if not data:
            return
        data = data[0]
        free_pe = Size(data['PSize'].lower())
        total_pe = int(data['SSize'])
        return Size(free_pe.bytes / total_pe)
