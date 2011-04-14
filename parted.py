import disk_maker
import os
import shlex
import subprocess
from subprocess import Popen, PIPE

class PartedInterface(object):
    '''
    Going to have to work with the parted command line tool due to time
    constaint. pyparted is not documented and messy.

    Once I can use libparted directly, I will move to that.
    '''
    def __init__(self, parted_path='/sbin/parted', device='/dev/sda'):
        self.parted_path = parted_path
        self.device = device
        self.parted = self.parted_path + ' --script ' + self.device + ' unit b'

    def get_table(self):
        return robo(self.parted + ' print')

    def get_size(self):
        table = self.get_table()
        for line in table:
            if 'Disk' in line:
                return line.split()[2].strip('B')
        return None

    def get_partitions(self):
        table = self.get_table
        parititions = list()
        for row in table:
            if row[0].isdigit():
                parititions.append(row.split())

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
        part_ids = [x[0] for x in self.get_partitions()]

        for part_ids in 

class PartedException(Exception):pass

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
