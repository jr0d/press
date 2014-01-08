import os
from cli import run
from structure import Size


class PartedInterface(object):
    """
    Going to have to work with the parted command line tool due to time
    constaint. pyparted is not documented and messy.

    Once I can use libparted directly, I will move to that.
    """

    def __init__(self, device, parted_path='/sbin/parted', partition_start=1048576, gap=1048576):
        self.parted_path = parted_path
        if not os.path.isfile(self.parted_path):
            raise PartedInterfaceException('%s does not exist.' % self.parted_path)
        self.device = device
        self.partition_start = partition_start
        self.gap = gap
        self.parted = self.parted_path + ' --script ' + self.device + ' unit b'

    def get_table(self):
        return run(self.parted + ' print').splitlines()

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

    def create_partition(self, part_type, part_size):
        """
        Get the size of the table.
        If there are existing partitions, get the end of the last partition
        and start from there. All partitions must have atleast a 40k buffer.
        Some believe that 128MiB buffer is appropriate for user partitions.

        For now, we will start the partitions at 40k and check the alignment.
        """
        table_size = Size(self.get_size())
        partitions = self.get_partitions()

        start = self.partition_start
        if partitions:
            start = int(partitions[-1][2].strip('B')) + self.gap * 10

        start = Size(start)
        end = start + part_size

        if end > table_size:
            raise PartedInterfaceException('The partition is too big.')

        command = self.parted + ' mkpart ' + ' %s %d %d' % (
            part_type, start.bytes, end.bytes)
        result = run(command)
        if result.returncode != 0:
            raise PartedException('Could not create partition.')


class PartedException(Exception): pass


class PartedInterfaceException(Exception): pass


