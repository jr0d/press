import os
from cli import run


class PartedInterface(object):
    """
    Going to have to work with the parted command line tool due to time
    consistent. pyparted is not documented and messy.

    Once I can use libparted directly, I will move to that.
    """

    def __init__(self, device, parted_path='/sbin/parted', partition_start=1048576, gap=1048576):
        self.parted_path = parted_path
        if not os.path.isfile(self.parted_path):
            raise PartedInterfaceException('%s does not exist.' % self.parted_path)
        self.device = device
        self.partition_start = partition_start
        self.gap = gap
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
                return line.split()[2].strip('B')
        return None

    def get_partitions(self):
        table = self.get_table()
        partitions = list()
        for row in table:
            if not row:
                continue
            if row.split()[0].isdigit():
                partitions.append(row.split())
        return partitions

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
        partitions = list()
        table = self.get_table(raw=True)
        part_data = table.split('\n\n')[1].splitlines()

        labels = part_data[0]

        return partitions


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
        cnt = 0
        part_ids = [x[0] for x in self.get_partitions()]
        if not part_ids:
            return cnt

        for part_id in part_ids:
            self.remove_partition(part_id)
            cnt += 1
        return cnt

    def set_label(self, label='gpt'):
        result = run(self.parted + ' mklabel ' + label)
        if result.returncode != 0:
            raise PartedException('Could not create filesystem label')

    def set_name(self, number, name):
        self.run_parted('set %d %s' % (number, name))

    @property
    def has_label(self):
        table = self.get_table()
        if not table:
            return False
        return True

    @staticmethod
    def _get_end(partitions):
        return int(partitions[-1][2].strip('B'))

    def create_partition(self, type_or_name, part_size):
        """
        Get the size of the table.
        If there are existing partitions, get the end of the last partition
        and start from there. All partitions must have atleast a 40k buffer.
        Some believe that 128MiB buffer is appropriate for user partitions.

        For now, we will start the partitions at 40k and check the alignment.

        type_or_name = primary/logical for msdos based partition tables. If a
        logical partition is requested, an extended lba partition will be
        created, if one does not yet exist, that fills the remainder of the disk.
        for gpt tables, the argument will be used as partition name.

        part_size = size of partition, in bytes.
        """
        table_size = self.get_size()
        partitions = self.get_partitions()

        label = self.get_label()

        start = self.partition_start

        if partitions:
            start = self._get_end(partitions) + self.gap * 10

        end = start + part_size

        if end > table_size:
            raise PartedInterfaceException('The partition is too big.')

        command = self.parted + ' mkpart ' + ' %s %d %d' % (
            type_or_name, start, end)
        result = run(command)
        if result.returncode != 0:
            raise PartedException('Could not create partition.')

        if label == 'gpt':
            # obviously we need to determine the new partition's id.
            self.set_name(1, type_or_name)


class PartedException(Exception):
    pass


class PartedInterfaceException(Exception):
    pass


