import logging
from press.helpers.mdadm import MDADM, MDADMError


class SoftwareRAID(object):
    raid_type = ''


class MDRaid(SoftwareRAID):
    raid_type = 'mdadm'

    def __init__(self, devname, level, members, spare_members=None, file_system=None, mount_point=None,
                 pv_name=None):
        """
        Logical representation of a mdadm controlled RAID
        :param devname: /dev/mdX
        :param level: 0, 1
        :param members: Partition objects that represent member disks
        :param spare_members: (optional) Partition objects that represent spare disks
        :param file_system: (optional) A file system object, if that is your intent
        :param mount_point: (optional) where to mount, needs file system
        :param pv_name: (optional) Am I a pv? if so, file_system and mount_point are ignored
        """

        self.devname = devname
        self.level = level
        self.members = members
        self.spare_members = spare_members
        self.file_system = file_system
        self.mount_point = mount_point
        self.pv_name = pv_name

        self.mdadm = MDADM()


    def create(self):
        pass

if __name__ == '__main__':
    from press.layout.filesystems.extended import EXT4
    mdraid = MDRaid('/dev/md0', 1, ['/dev/loop0p1', '/dev/loop1p1'])

    boot_fs = EXT4(label='BOOT')
    mdadm = MDADM()
    mdraid = MDRaid('/dev/md0', level=1, members=['/dev/loop0p1', '/dev/loop1p1'], file_system=boot_fs,
                    mount_point='/boot')
