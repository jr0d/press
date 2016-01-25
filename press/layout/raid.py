import logging
from press.exceptions import PressCriticalException
from press.helpers.mdadm import MDADM
from press.layout.size import Size


log = logging.getLogger(__name__)


class SoftwareRAID(object):
    raid_type = ''


class MDRaid(SoftwareRAID):
    raid_type = 'mdadm'

    def __init__(self, devname, level, members, spare_members=None, size=0, file_system=None, mount_point=None,
                 fsck_option=0, pv_name=None):
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
        self.spare_members = spare_members or []
        self.file_system = file_system
        self.mount_point = mount_point
        self.pv_name = pv_name
        self.size = Size(0)
        self.allocated = False
        self.mdadm = MDADM()

    @staticmethod
    def _get_partition_devnames(members):
        disks = []

        for partition in members:
            if not partition.allocated:
                raise PressCriticalException('Attempted to use unlinked partition')
            disks.append(partition.devname)

        return disks

    def calculate_size(self):
        for member in self.members:
            if not member.allocated:
                raise PressCriticalException('Member is not allocated, cannot calculate size')

        if self.level == 0:
            accumulated_size = Size(0)
            for member in self.members:
                accumulated_size += member.size
            self.size = accumulated_size

        if self.level == 1:
            self.size = self.members[0].size

    def create(self):
        """
        """

        member_partitions = self._get_partition_devnames(self.members)
        spare_partitions = self._get_partition_devnames(self.spare_members)

        log.info('Building Software RAID %s' % self.devname)
        self.mdadm.create(self.devname,
                          self.level,
                          member_partitions,
                          spare_partitions,
                          )

    def generate_fstab_entry(self):
        """
        If there is a file system on the volume, we need to be able to generate and fstab
        :return:
        """
        assert self
        pass

    def __repr__(self):
        return '%s : %s' % (self.devname, self.members)
