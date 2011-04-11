import disk_maker

from subprocess import Popen, PIPE

class PartedInterface(object):
    '''
    Going to have to work with the parted command line tool due to time
    constaint. pyparted is not documented and messy. 
    '''
    def __init__(self, parted_path='/sbin/parted', device='/dev/sda'):
        self.parted_path = parted_path
        self.device = device
        self.parted = self.parted_path + ' --script ' + self.device

    def print_table(self):
        print
        execute(self.parted + ' print')
                

def execute(command=''):
    p = Popen(command, shell=True)
    status = os.waitpid(p.pid, 0)[1]
    return status

def robo(command=''):

