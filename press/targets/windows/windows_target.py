import logging

from press.helpers.cli import run
from press.targets import Target


log = logging.getLogger(__name__)


class WindowsTarget(Target):
    name = 'windows'
    dev_name = ''

    @property
    def bootloader_configuration(self):
        return self.press_configuration.get('bootloader')

    def get_file_name(self):
        url = self.press_configuration.get('image').get('url')
        return url.split('/')[-1]

    def get_wim_index(self):
        return self.press_configuration.get('image').get('wim_index')

    def disk_target(self):
        _target = self.bootloader_configuration.get('target', 'first')
        if _target == 'first':
            return self.layout.disks.keys()[0]
        return _target

    def get_dev_name(self):
        self.dev_name = '{}1'.format(self.disk_target())

    def wimapply(self):
        file_name = self.get_file_name()
        wim_index = self.get_wim_index()
        log.info('Applying windows image {}'.format(file_name))
        command = "wimapply {0} {1} {2}".format(self.join_root(file_name),
                                                wim_index,
                                                self.dev_name)
        res = run(command)
        if res.returncode:
            log.error("Failed to apply windows files on "
                      "device {}".format(self.dev_name))
        else:
            log.info('Applied windows files on device {}'.format(self.dev_name))

    def write_windows_boot_record(self):
        log.info("Writting windows boot record")
        command = "ms-sys -w {}".format(self.dev_name)
        res = run(command)
        if res.returncode:
            log.error("Failed to write windows boot record "
                      "on device {}".format(self.dev_name))
        else:
            log.info('Windows boot record was added on '
                     'device {}'.format(self.dev_name))

    def install_mbr(self):
        command = "dd if=/usr/share/syslinux/mbr.bin " \
                  "of={}".format(self.dev_name[:-1])
        res = run(command)
        if res.returncode:
            log.error("Failed to run command {}".format(command))

    def run(self):
        self.get_dev_name()
        self.wimapply()
        self.write_windows_boot_record()
        self.install_mbr()

