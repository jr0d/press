from press.cli import run
import logging
import os
import string
import crypt
import random


log = logging.getLogger(__name__)

# Generate a random password for security.
passwd = ''.join(
    map(lambda x: random.choice(list(string.ascii_letters)), range(25)))

DEFAULTS = \
    {'auth':
         {'algorithm': 'sha512',
          'users':
              {'root':
                   {
                       'authorized_keys': None,
                       'home': '/root',
                       'password': passwd,
                       'password_options': [
                           {
                               'encrypted': False
                           }
                       ]
                   }
              }
         },
     'bootloader':
         {
             'type': None,
             'target': None,
             'options': None,
         }
    }

class Chroot(object):
    """
    Base Post Class.
    """

    def __init__(self, newroot, config, disks):
        """
        Starts post process.

        :param newroot: String path to our new root.
        :param config: a dict with all our configuration.
        :param disks: Layout.disks, an OrderedDict containing Disk objects indexed by devname
        """
        self.newroot = newroot
        self.config = self.__generate_config(config)

        log.debug('Running chroot from configuration: %s' % self.config)

        self.real_root = os.open('/', os.O_RDONLY)
        self.disks = disks
        os.chroot(newroot)
        os.chdir('/')

    @staticmethod
    def __generate_config(config):
        """
        Generates config by updating DEFAULTS with config.
        """
        auth = dict(auth=config.get('auth', {}))
        bootloader = dict(bootloader=config.get('bootloader', {}))
        DEFAULTS.update(auth)
        DEFAULTS.update(bootloader)
        return DEFAULTS

    def __exit__(self):
        """
        Exits an active chroot
        """
        os.fchdir(self.real_root)
        os.chroot('.')
        os.chdir('/')

    @staticmethod
    def generate_salt512(length=12):
        """
        Generate a random salt512
        """
        pool = [chr(x) for x in range(48, 122) if chr(x).isalnum()]
        chars = list()
        while len(chars) < length:
            chars.append(random.choice(pool))
        return '$6$%s$' % ''.join(chars)

    @staticmethod
    def generate_hash(x, salt):
        """
        Generate a hash using salt
        """
        return crypt.crypt(x, salt)

    @staticmethod
    def __reboot():
        """
        Reboots the system.
        """
        log.debug('Rebooting system.')
        run('reboot', raise_exception=True)

    def __groupadd(self, group, gid):
        """
        Creates a group from configuration and build options.
        """
        command = 'groupadd %s -g %s' % (group, gid)
        log.info(command)
        run('groupadd %s -g %s' % (group, gid), raise_exception=True)

    def __useradd(self, username, options):
        """
        Creates a users from configuration and build options.
        """
        command = 'useradd %s -m %s' % (username, options)
        log.info(command)
        run(command, raise_exception=True)

    def __passwd(self, username, password, encrypted=False):
        """
        Set the passwords for users using config.
        """
        log.info('Setting password for %s' % username)
        if not encrypted:
            salt = self.generate_salt512()
            encrypted_password = self.generate_hash(password, salt)
        else:
            encrypted_password = password
        command = "usermod -p %s %s" % (encrypted_password, username)
        run(command, raise_exception=True)

    def add_users(self):
        """
        Add users from configuration.
        """
        log.debug('Running add_users')

        for user, data in self.config['auth']['users'].items():
            options = list()
            # if this is the root user, lets set password then skip rest.
            if user == 'root':
                if data.get('password'):
                    self.__passwd('root',
                                  data['password'],
                                  data.get('password_options', dict()).get('encrypted') or False)
                continue

            # check for our useradd options in config.
            if data.get('home'):
                options.append('-d %s' % data['home'])

            if data.get('shell'):
                options.append('-s %s' % data['shell'])

            if data.get('uid'):
                options.append('-u %s' % data['uid'])

            if data.get('gid'):
                self.__groupadd(user, data['gid'])  # create our group.
                options.append('-g %s' % data['gid'])

            # time to build all options into a string separated by spaces.
            options = ' '.join(options)

            # create users with useradd command
            self.__useradd(user, options)

            # set password with passwd command
            if data.get('password'):
                self.__passwd(user,
                              data['password'],
                              data.get('password_options', dict()).get('encrypted') or False)

    def install_bootloader(self, disk):
        """
        Install bootloader on disk.

        :param disk: Disk as a string /dev/sda
        """
        return NotImplemented

    def apply(self):
        """
        Run our entire chroot process.
        """
        return NotImplemented

