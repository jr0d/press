import structure
import os
import shlex
import subprocess
from subprocess import Popen, PIPE
from structure import Size

class PartedInterface(object):
    '''
    Going to have to work with the parted command line tool due to time
    constaint. pyparted is not documented and messy.

    Once I can use libparted directly, I will move to that.
    '''
    __gpt_alignment__ = 1048576
    __partition_gap__ = 1048576
    
    def __init__(self, parted_path='/sbin/parted', device='/dev/sda'):
        self.parted_path = parted_path
        if not os.path.isfile(self.parted_path):
            raise PartedInterfaceException('%s does not exist.' % self.path)
        self.device = device
        self.parted = self.parted_path + ' --script ' + self.device + ' unit b'

    def get_table(self):
        return robo(self.parted + ' print')

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
        '''
        Uses run to spawn the process and looks for the return val.
        '''
        command = self.parted + ' rm ' + str(partition_number)

        ret = run(command)

        if ret != 0:
            raise PartedException(
                    'Could not remove partition: %d' % partition_number)

    def wipe_table(self):
        cnt = 0
        part_ids = [x[0] for x in self.get_partitions()]
        if not part_ids:
            return cnt

        for part_id in part_ids:
                self.remove_partition(part_id)
                cnt = cnt + 1
        return cnt

    def set_label(self, label='gpt'):
        ret = run(self.parted + ' mklabel ' + label)
        if ret != 0:
            raise PartedException('Could not create filesystem label')

    def create_partition(self, part_type, part_size):
        '''
        Get the size of the table. 
        If there are existing partitions, get the end of the last partition
        and start from there. All partitions must have atleast a 40k buffer.
        Some believe that 128MiB buffer is appropriate for user partitions. 

        For now, we will start the partitions at 40k and check the alignment.
        '''
        table_size = Size(self.get_size())
        partitions = self.get_partitions()

        start = self.__gpt_alignment__
        if partitions:
            start = int(partitions[-1][2].strip('B')) + \
            self.__partition_gap__ * 10

        start = Size(start)
        end = start + part_size

        if end > table_size:
            raise PartedInterfaceException('The partition is too big.')

        command = self.parted + ' mkpart ' + ' %s %s %s' % (
                part_type, start.tostring(), end.tostring())
        ret = run(command)
        if ret != 0:
            raise PartedException('Could not create partition.')


class PartedException(Exception):pass
class PartedInterfaceException(Exception):pass

def execute(command=''):
    p = Popen(command, shell=True)
    status = os.waitpid(p.pid, 0)[1]
    return status

def robo(command='', output_descriptor='stdout', bufsize=1048576):
    '''
    run command and return a list containing each line of output.
    Change this to:

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    '''
    if output_descriptor == 'stdout' or output_descriptor != 'stderr':
        pipe = Popen(command, shell=True, bufsize=bufsize, stdout=PIPE).stdout
    
    elif output_descriptor == 'stderr':
        pipe = Popen(command, shell=True, bufsize=bufsize, stderr=PIPE).stderr

    return pipe.read().splitlines()

def run(command=''):
    return subprocess.call(shlex.split(command), stdout=PIPE, stderr=PIPE)
