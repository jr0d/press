import logging
import os

from press.helpers.cli import run_chroot

log = logging.getLogger('press.targets')


class Chroot(object):
    def __init__(self, root, staging_dir):
        self.root = root
        self.staging_dir = staging_dir

    def __call__(self, command, raise_exception=False, quiet=False):
        return run_chroot(command, root=self.root, staging_dir=self.staging_dir,
                          raise_exception=raise_exception, quiet=quiet)


class VendorRegistry(type):
    targets = dict()

    def __new__(mcs, name, bases, attrs):
        new_cls = type.__new__(mcs, name, bases, attrs)
        name = attrs.get('name')
        if name:
            log.info('Registered post handler: %s' % name)
            mcs.targets[name] = new_cls
        return new_cls

class Target(object):
    __metaclass__ = VendorRegistry

    name = ''

    def __init__(self, press_configuration, disks, root, chroot_staging_dir):
        self.press_configuration = press_configuration
        self.disks = disks
        self.root = root
        self.chroot_staging_dir = chroot_staging_dir
        self.chroot = Chroot(self.root, self.chroot_staging_dir)

    def join_root(self, path):
        path = path.lstrip('/')
        return os.path.join(self.root, path)

    @classmethod
    def probe(cls, deployment_root):
        """
        function is called to identify
        :return:
        """
        assert os.path.isdir(deployment_root)
        return False

    def run(self):
        """
        Called by press, overrides should take care to call the run function of their parent unless the override
        is meant to replace all of the parents functionality

        eg:
            class EnterpriseLinux7(Redhat):
                def run(self):
                    super(EnterpriseLinux7, self).run()
                    el7_function()
        :return:
        """
        return self


class GeneralPostTargetError(Exception):
    pass
