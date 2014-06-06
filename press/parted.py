import os
from cli import run


class PartedInterface(object):
    """
    Going to have to work with the parted command line tool due to time
    consistent. pyparted is not documented and messy.

    Once I can use libparted directly, I will move to that.
    """

    def __init__(self, device, parted_path='/sbin/parted', partition_start=1048576, gap=1048576,
                 alignment=4096):
        self.parted_path = parted_path
        if not os.path.isfile(self.parted_path):
            raise PartedInterfaceException('%s does not exist.' % self.parted_path)
        self.device = device
        self.partition_start = partition_start
        self.gap = gap
        self.alignment = alignment
        if gap % alignment:
            raise PartedException('Requested alignment is not a multiple of gap.')

        self.parted = self.parted_path + ' --script ' + self.device + ' unit b '

    def run_parted(self, command, raise_on_error=True):
        """
        parted does not use meaningful return codes. It pretty much returns 1 on
        any error and then prints an error message on to standard error stream.
        """
        result = run(self.parted + command)
        if result and raise_on_error:
            raise PartedException(result.stderr)
        return result

    def make_partition(self, type, start, end):
        command = 'mkpart %s %d %d' % (type, start, end)
        return self.run_parted(command)

    def get_table(self, raw=False):
        result = self.run_parted('print', raise_on_error=False)
        if result.returncode:
            if 'unrecognised disk label' in result.stderr:
                pass
            else:
                raise PartedException(result.stderr)
        if raw:
            return result
        return result.splitlines()

    def get_size(self):
        table = self.get_table()
        for line in table:
            if 'Disk' in line and line.split()[2][0].isdigit():
                return int(line.split()[2].strip('B'))

    def _get_info(self, term):
        table = self.get_table()
        for line in table:
            if term in line:
                return line.split(':')[1].strip()

    def get_model(self):
        return self._get_info('Model')

    def get_sector_size(self):
        size = self._get_info('Sector size (logical/physical)')
        logical, physical = size.split('/')
        logical = int(logical[:-1])
        physical = int(physical[:-1])
        return dict(logical=logical, physical=physical)

    def get_disk_flags(self):
        return self._get_info('Disk Flags')

    def get_label(self):
        return self._get_info('Partition Table')

    @property
    def device_info(self):
        info = dict()
        info['model'] = self.get_model()
        info['device'] = self.device
        info['size'] = self.get_size()
        info['sector_size'] = self.get_sector_size()
        info['partition_table'] = self.get_label()
        info['disk_flags'] = self.get_disk_flags()
        return info

    @property
    def partitions(self):
        p = list()
        table = self.get_table(raw=True)
        partition_type = self.get_label()

        if partition_type == 'unknown':
            return p

        part_data = table.split('\n\n')[1].splitlines()[1:]

        if not part_data:
            return p

        for part in part_data:
            part = part.split()
            part_info = dict()
            part_info['number'] = int(part[0].strip())
            part_info['start'] = int(part[1].strip('B'))
            part_info['end'] = int(part[2].strip('B'))
            part_info['size'] = int(part[3].strip('B'))

            if partition_type == 'msdos':
                part_info['type'] = part[4]
            p.append(part_info)

        return p

    @property
    def last_partition(self):
        partitions = self.partitions
        if not partitions:
            return None
        return partitions[-1]

    @property
    def extended_partition(self):
        if self.get_label() != 'msdos':
            return

        partitions = self.partitions

        if not partitions:
            return

        for part in partitions:
            if part['type'] == 'extended':
                return part

    def remove_partition(self, partition_number):
        """
        Uses run to spawn the process and looks for the return val.
        """
        command = self.parted + ' rm ' + str(partition_number)

        result = run(command)

        if result.returncode != 0:
            raise PartedException(
                'Could not remove partition: %d' % partition_number)

    def wipe_table(self):
        extended_partition = self.extended_partition
        if extended_partition:
            self.remove_partition(extended_partition['number'])

        for partition in self.partitions:
            self.remove_partition(partition['number'])

    def set_label(self, label='gpt'):
        result = run(self.parted + ' mklabel ' + label)
        if result.returncode != 0:
            raise PartedException('Could not create filesystem label')

    def set_name(self, number, name):
        self.run_parted('set %d %s' % (number, name))

    def set_boot_flag(self, number):
        self.run_parted('set %d boot on' % number)

    def set_lvm_flag(self, number):
        self.run_parted('set %d lvm on' % number)

    @property
    def has_label(self):
        table = self.get_table()
        if not table:
            return False
        return True

    def create_partition(self, type_or_name, part_size, boot_flag=False, lvm_flag=False):
        """

        For now, we will start the partitions at 1MiB and check the alignment.

        type_or_name: primary/logical for msdos based partition tables. If a
        logical partition is requested, an extended lba partition will be
        created, if one does not yet exist, that fills the remainder of the disk.
        for gpt tables, the argument will be used as partition name.

        part_size: size of partition, in bytes.

        return: The new partition id
        """

        table_size = self.get_size()

        label = self.get_label()

        start = self.partition_start

        partition_number = 1

        last_partition = self.last_partition

        if last_partition:
            aligned = \
                last_partition['end'] + (self.alignment - (last_partition['end'] % self.alignment))
            start = aligned + self.gap
            partition_number = last_partition['number'] + 1

        end = start + part_size

        if end >= table_size:
            raise PartedInterfaceException('The partition is too big.')

        if type_or_name == 'logical' and label == 'msdos':
            if not self.extended_partition:
                self.make_partition('extended', start, table_size - 1)
                start += self.gap
                end = start + part_size
                partition_number = 5

        self.make_partition(type_or_name, start, end)

        if label == 'gpt':
            # obviously we need to determine the new partition's id.
            self.set_name(partition_number, type_or_name)

        if boot_flag:
            self.set_boot_flag(partition_number)

        if lvm_flag:
            self.set_lvm_flag(partition_number)

        return partition_number

    def remove_mbr(self):
        mbr_bytes = 512
        command = 'dd if=/dev/zero of=%s bs=%d count=1' % (self.device, mbr_bytes)
        run(command)

    def remove_gpt(self):
        """
        512 Fake MBR
        512 GPT Header
        16KiB Primary Table
        16KiB Backup Table
        """
        gpt_bytes = 33792
        command = 'dd if=/dev/zero of=%s bs=%d count=1' % (self.device, gpt_bytes)
        run(command)


class PartedException(Exception):
    pass


class PartedInterfaceException(Exception):
    pass
