import logging
import uuid

from press.helpers import deployment
from press.helpers.cli import run
from press.helpers.sysfs_info import has_efi
from press.targets import Target


log = logging.getLogger(__name__)


class WindowsTarget(Target):
    name = 'windows'
    dev_name = ''

    # Current values to replace in the BCD template
    BCD_DISK_GUID = None
    BCD_EFI_PART_GUID = None
    BCD_C_PART_GUID = None

    # The path of the BCD file to edit
    BCD_PATH = None

    EFI_PARTITION_MOUNT_POINT = '/mnt/efi'

    @property
    def bootloader_configuration(self):
        return self.press_configuration.get('bootloader')

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

    @staticmethod
    def replace_guid(data, old, new):
        current_pos = 0
        replace_count = 0
        while True:
            try:
                idx = data[current_pos:].index(old)
            except ValueError:
                break
            replace_count += 1
            for i in range(16):
                data[current_pos+idx+i] = new[i]
            print(uuid.UUID(bytes_le=bytes(data[current_pos+idx:current_pos+idx+16])))
            current_pos = current_pos + 16 + idx
        return replace_count

    def update_bcd_guids(self, data, new_disk_guid, new_efi_guid, new_c_guid):
        self.replace_guid(data, self.BCD_DISK_GUID, new_disk_guid)
        self.replace_guid(data, self.BCD_EFI_PART_GUID, new_efi_guid)
        self.replace_guid(data, self.BCD_C_PART_GUID, new_c_guid)

    def mount_efi_partition(self):
        pass

    def umount_efi_partition(self):
        pass

    def copy_efi_data(self):
        deployment.recursive_makedir('/mnt')

    def update_and_copy_bcd_hive(self):
        pass

    def get_bcd_data(self):
        with open(self.BCD_PATH, "rb") as fp:
            return bytearray(fp.read())

    def run(self):
        if has_efi():
            pass
        else:
            self.write_windows_boot_record()
            self.install_mbr()
