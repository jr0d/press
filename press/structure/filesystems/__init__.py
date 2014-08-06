import uuid


class FileSystem(object):
    fs_type = ''
    default_mount_options = ['default']

    def __init__(self, fs_label=None, mount_options=None):
        self.fs_label = fs_label
        self.mount_options = mount_options or self.default_mount_options
        self.fs_uuid = uuid.uuid4()

    def create(self, device):
        """

        :param device:
        :raise NotImplemented:
        """
        raise NotImplemented('%s base class should not be used.' % self.__name__)

    def __post_create(self, device):
        self.fs_uuid = get_uuid(device)

    def generate_mount_options(self):
        if hasattr(self, 'mount_options'):
            options = self.mount_options
        else:
            options = self.default_mount_options

        return ','.join(options)

    def __repr__(self):
        return self.fs_type or 'Undefined'



