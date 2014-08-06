import logging
from collections import OrderedDict

from press import helpers
from press.parted import PartedInterface, NullDiskException
from press.lvm import LVM
from press.udev import UDevHelper
from press.structure.disk import Disk
from press.structure.lvm import VolumeGroup
from press.structure.size import Size

from press.structure.exceptions import (
    PhysicalDiskException,
    LayoutValidationError,
    GeneralValidationException
)

log = logging.getLogger(__name__)


class Layout(object):
    """The highest level class.
    """

    def __init__(self,
                 use_fibre_channel=True, use_loop_devices=True, loop_only=False,
                 parted_path='/sbin/parted',
                 default_partition_start=1048576, default_alignment=1048576,
                 disk_association='explicit'):
        """
        Docs, maybe later

        :param use_fibre_channel:
        :param use_loop_devices:
        :param loop_only:
        :param parted_path:
        :param default_partition_start:
        :param default_alignment:
        :param disk_association: explicit: path must be associated with Disk object
                          first: Use only the first available disk, subsequent calls to add_disk
                            trigger an exception
                          any: The first available disk is used that can accommodate the
                            partition table

        :ivar self.committed: False on __init__, True after calling apply()
        """

        self.committed = False
        self.fc_enabled = use_fibre_channel
        self.loop_enabled = use_loop_devices
        self.parted_path = parted_path
        self.default_partition_start = default_partition_start
        self.default_alignment = default_alignment
        self.disk_association = disk_association
        self.udev = UDevHelper()
        self.udisks = self.udev.discover_valid_storage_devices(self.fc_enabled,
                                                               self.loop_enabled)
        if loop_only:
            self.udisks = [udisk for udisk in self.udisks if 'loop' in udisk['DEVNAME']]

        if not self.udisks:
            raise PhysicalDiskException('There are no valid disks.')

        self.disks = OrderedDict()
        self.__populate_disks()
        if not self.disks:
            raise PhysicalDiskException('There are no valid disks.')

        self.volume_groups = list()
        self.lvm = LVM()

    def __populate_disks(self):
        for udisk in self.udisks:
            device = udisk.get('DEVNAME')
            try:
                parted = PartedInterface(device, self.parted_path)
            except NullDiskException:
                log.debug('NullDiskException for %s' % device)
                continue
            size = parted.get_size()
            disk = Disk(devname=device,
                        devlinks=udisk.get('DEVLINKS'),
                        devpath=udisk.get('DEVPATH'), size=size)
            self.disks[device] = disk

    def find_device_by_ref(self, ref):
        """

        :param ref:
        :return:
        """
        for disk in self.disks.values():
            if ref == disk.devname:
                return disk
            if ref == disk.devpath:
                return disk
            for link in disk.devlinks:
                if ref == link:
                    return disk

    def find_device_by_size(self, size):
        """

        :param size:
        :return:
        """
        for disk in self.disks.values():
            if size < disk.size:
                return disk

    def _get_parted_interface_for_allocated_device(self, disk):
        """

        :param disk:
        :return: :raise LayoutValidationError:
        """
        if not disk.partition_table:
            raise LayoutValidationError('Disk is not allocated')
        return PartedInterface(device=disk.devname,
                               parted_path=self.parted_path,
                               partition_start=disk.partition_table.partition_start.bytes,
                               alignment=disk.partition_table.alignment.bytes)

    @property
    def allocated(self):
        l = list()
        for disk in self.disks.values():
            if disk.partition_table:
                l.append(disk)
        return l

    @property
    def unallocated(self):
        l = list()
        for disk in self.disks.values():
            if not disk.partition_table:
                l.append(disk)
        return l

    def add_partition_table_from_model(self, partition_table):
        unallocated = self.unallocated
        if not unallocated:
            raise PhysicalDiskException('There are more available disks')

        if partition_table.disk == 'first':
            disk = unallocated[0]

        elif partition_table.disk == 'any':
            disk = self.find_device_by_size(partition_table.allocated_space)
            if not disk:
                raise PhysicalDiskException('There is no suitable disk, table is too big')

        else:
            disk = self.find_device_by_ref(partition_table.disk)
            if not disk:
                raise PhysicalDiskException('Could not associate disk, %s was not found' %
                                            partition_table.disk)

        disk.new_partition_table(partition_table.type, partition_start=self.default_partition_start,
                                 alignment=self.default_alignment)

        for partition in partition_table.partitions:
            disk.partition_table.add_partition(partition)

    def find_partition_devname(self, disk, partition_id):
        # make this part of UDevHelper?
        partitions = self.udev.find_partitions(disk.devname)
        for partition in partitions:
            if int(partition.get('UDISKS_PARTITION_NUMBER', -1)) == partition_id:
                return partition.get('DEVNAME')

    def add_volume_group_from_model(self, model_vg):
        for pv in model_vg.physical_volumes:
            if not pv.reference.lvm:
                raise LayoutValidationError('Reference partition is not flagged for LVM use')
            if not isinstance(pv.reference.size, Size) and not pv.size.bytes:
                raise LayoutValidationError('Reference partition has not be allocated')
        real_vg = VolumeGroup(model_vg.name, model_vg.physical_volumes, model_vg.pe_size)
        for lv in model_vg.logical_volumes:
            real_vg.add_logical_volume(lv)
        self.volume_groups.append(real_vg)

    def apply(self):
        """Lots of logging here
        """
        for disk in self.allocated:
            parted = self._get_parted_interface_for_allocated_device(disk)
            partition_table = disk.partition_table
            parted.set_label(partition_table.type)
            for partition in partition_table.partitions:
                partition_id = parted.create_partition(partition.name,
                                                       partition.size.bytes,
                                                       boot_flag=partition.boot,
                                                       lvm_flag=partition.lvm)

                partition.devname = self.udev.monitor_partition_by_devname(partition_id)
                partition.partition_id = partition_id

                if not partition.devname:
                    log.error('%s %s %s' % (partition.devname, disk, partition_id))
                    raise PhysicalDiskException('Could not relate partition id to devname')

                if partition.file_system:
                    partition.file_system.create(partition.devname)

            for volume_group in self.volume_groups:
                devnames = list()
                for pv in volume_group.physical_volumes:
                    if not pv.reference.devname:
                        raise LayoutValidationError('devname is not populated, and it should be')
                    devnames.append(pv.reference.devname)
                    self.lvm.pvcreate(pv.reference.devname)
                self.lvm.vgcreate(volume_group.name, devnames, volume_group.pe_size.bytes)
                for lv in volume_group.logical_volumes:
                    self.lvm.lvcreate(lv.extents, volume_group.name, lv.name)
        self.committed = True

    def generate_fstab(self, method='UUID'):
        """
        This generates an fstab for this partition layout

        :param method: UUID, DEVNAME, or LABEL
        :return: (str) the generated fstab
        """

        supported_methods = ['DEVNAME', 'UUID', 'LABEL']

        if method not in supported_methods:
            raise GeneralValidationException('Method not supported')

        log.info('Generating %s partition table.' % method)
        header = '# Generated by Press v' + str(helpers.package.get_press_version())
        fstab = ''

        for disk in self.allocated:
            parted = self._get_parted_interface_for_allocated_device(disk)
            parted.get_table()

            partition_table = disk.partition_table

            for partition in partition_table.partitions:
                if not partition.file_system:
                    continue

                uuid = partition.file_system.fs_uuid
                if not uuid:
                    continue

                label = partition.file_system.fs_label
                if (method == 'LABEL') and not label:
                    log.debug(
                        'Missing label, offender: %s' % partition.devname)

                options = partition.file_system.generate_mount_options()
                dump = '0'
                fsck_option = partition.fsck_option

                if method == 'UUID':
                    fstab += '# DEVNAME=%s\tLABEL=%s\nUUID=%s\t\t' % (partition.devname, label or '', uuid)
                elif method == 'LABEL' and label:
                    fstab += '# DEVNAME=%s\tUUID=%s\nLABEL=%s\t\t' % (partition.devname, uuid, label)
                else:
                    fstab += '# UUID=%s\tLABEL=%s\n%s\t\t' % (uuid, label or '', partition.devname)
                fstab += '%s\t\t%s\t\t%s\t\t%s %s\n\n' % (
                    partition.mount_point, partition.file_system, options, dump, fsck_option)

        return header + '\n\n' + fstab

    def parse_partitions(self):
        for disk in self.allocated:
            partition_table = disk.partition_table
            mounts = dict()
            for partition in partition_table.partitions:
                if partition.mount_point:
                    p_depth = self.mount_depth(partition.mount_point)
                    if mounts.get(p_depth):
                        mounts[p_depth] += [(partition.devname, partition.mount_point)]
                    else:
                        mounts[p_depth] = [(partition.devname, partition.mount_point)]
            return mounts

    def mount_depth(self, mount_point, depth=1):
        if mount_point == '/':
            return 0
        if mount_point[1:].find('/') == -1:
            return depth
        else:
            depth += 1
            mount_point = mount_point[mount_point[1:].find('/') + 1:]
            return self.mount_depth(mount_point, depth)

    def mount_disk(self, base_dir='/mnt/press'):

        mounts = self.parse_partitions()

        for depth in sorted(mounts):
            for mount in mounts[depth]:
                devname = mount[0]
                mount_point = mount[1]
                log.info('Making directory %s' % base_dir + mount_point)
                helpers.deployment.mkdir(base_dir + mount_point)
                log.info('Mounting %s on %s' % (devname, base_dir + mount_point))
                helpers.deployment.mount('%s %s' % (devname, base_dir + mount_point))

        log.info('Creating and placing fstab in /etc/fstab_rs')
        helpers.deployment.mkdir(base_dir + '/etc')
        helpers.file.write(base_dir + '/etc/fstab_rs', self.generate_fstab())

        log.info("Drive is mounted and ready for OS image.")
