
from press.cli import run
import logging
import os


log = logging.getLogger(__name__)


class Chroot(object):
    """
    Base Post Class.
    """

    def __init__(self, newroot, config):
        """
        Starts post process.

        :param newroot: String path to our new root.
        :parma config: a dict with all our configuration.
        """
        self.config = config
        self.__bind_mount(prefix='/mnt/press')
        self.real_root = os.open('/', os.O_RDONLY)
        os.chroot(newroot)
        os.chdir('/')

    def __exit__(self):
        """
        Exits an active chroot
        """
        if self.real_root:
            os.fchdir(self.real_root)
            os.chroot('.')
            os.chdir('/')
        self.__unmount_prefix(prefix='/mnt/press')
        self.__reboot()

    @staticmethod
    def __bind_mount(prefix, mount_points=('/proc', '/dev', '/sys')):
        """
        Bind mounts the base locations to prefix

        :parma prefix: The prefix on where we wish to bind mount.
        :param mount_points: a list/tuple of mount_points to bind on prefix.
        """
        for mount_point in mount_points:
            log.debug('Bind mounting %s to %s%s' % (
                mount_point, prefix, mount_point))
            run('mount --rbind %s %s%s' % (mount_point, prefix, mount_point),
                raise_exception=True)

    @staticmethod
    def __unmount_prefix(prefix):
        """
        Use lazy unmount to remove everything under prefix.

        :parma prefix: The prefix on where we wish to unmount.
        """
        log.debug('Unmounting everything under %s' % prefix)
        run('umount -l %s' % prefix, raise_exception=True)

    def __reboot(self):
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
        log.debug(command)
        run('groupadd %s -g %s' % (group, gid), raise_exception=True)


    def __useradd(self, username, options):
        """
        Creates a users from configuration and build options.
        """
        command = 'useradd %s -m %s' % (username, options)
        log.debug(command)
        run(command, raise_exception=True)

    def __passwd(self, username, password):
        """
        Set the passwords for users using config.
        """
        command = 'echo %s:%s | chpasswd' % (username, password)
        log.debug(command.replace(password, '*********'))
        run(command, raise_exception=True)

    def add_users(self):
        """
        Add users from configuration.
        """
        log.debug('Running add_users')
        options = []

        if 'auth' not in self.config:
            log.warning('Missing auth section in config.')
            return

        if 'users' not in self.config['auth']:
            log.warning('Missing users section in config.')
            return

        for user, data in self.config['auth']['users'].items():

            # if this is the root user, lets set password then skip rest.
            if user == 'root':
                if data.get('password'):
                    # TODO use password_options for encrypted passwords.
                    self.__passwd('root', data['password'])
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
            # TODO use password_options for encrypted passwords.
            if data.get('password'):
                self.__passwd(user, data['password'])

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

