class FileSystem(object):
    fs_type = ''
    default_mount_options = ['default']

    def __init__(self, fs_label=None, mount_options=None, fsck_option=0):
        self.fs_label = fs_label
        self.mount_options = mount_options or self.default_mount_options
        self.fsck_option = fsck_option

    def create(self, device):
        """

        :param device:
        :raise NotImplemented:
        """
        raise NotImplemented('%s base class should not be used.' % self.__name__)

    def generate_mount_options(self):
        if hasattr(self, 'mount_options'):
            options = self.mount_options
        else:
            options = self.default_mount_options

        return ','.join(options)

    def __repr__(self):
        return self.fs_type or 'Undefined'