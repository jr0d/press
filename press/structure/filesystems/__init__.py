import time

class FileSystem(object):
    fs_type = ''

    def create(self, device):
        """

        :param device:
        :raise NotImplemented:
        """
        raise NotImplemented('%s base class should not be used.' % self.__name__)

    def __repr__(self):
        return self.fs_type or 'Undefined'

    def get_uuid(self, device, retry=5):
        """
        UDEV sometimes takes a moment to have UUID, so this will sleep and repeat trying till it does.
        :param device: This is the device ie. /dev/sda1
        :param sleep:  This is a variable for how long to sleep before retries
        :return: Returns the UUID and LABEL.
        """
        count = 0
        sleep = 1
        while True:
            udev_device = self.udev.get_device_by_name(device)
            if 'ID_FS_UUID' in udev_device:
                if 'ID_FS_LABEL' in udev_device:
                    label = str(udev_device['ID_FS_LABEL'])
                else:
                    label = None
                return str(udev_device['ID_FS_UUID']), label
            print 'UDEV still settling, sleeping %s seconds' % sleep
            time.sleep(sleep)
            count += 1
            sleep += count

