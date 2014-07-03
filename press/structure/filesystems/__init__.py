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