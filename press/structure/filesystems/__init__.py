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

    def get_uuid(self, device):
        """
        Get UUID and LABEL from blkid.
        :param device: This is the device ie. /dev/sda1
        :return: Returns the UUID and LABEL.
        """
        uuid = run('blkid -o value -s UUID %s' % device).strip('\n')
        label = run('blkid -o value -s LABEL %s' % device).strip('\n')
        return uuid, label

