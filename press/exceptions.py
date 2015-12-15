class FileSystemCreateException(Exception):
    def __init__(self, fs_type, fs_command, attr_str):
        self.fs_type = fs_type
        self.fs_command = fs_command
        self.attr_str = attr_str


class FileSystemFindCommandException(Exception):
    """
    Raised when FileSystem class cannot discover
    """


class PartitionValidationError(Exception):
    pass


class LayoutValidationError(Exception):
    pass


class LVMValidationError(Exception):
    pass


class PhysicalDiskException(Exception):
    pass


class GeneralValidationException(Exception):
    pass


class GeneratorError(Exception):
    pass


class ConfigurationError(Exception):
    pass


class PressCriticalException(Exception):
    pass


class ImageValidationException(Exception):
    pass


class NetworkConfigurationError(ConfigurationError):
    pass


class HookError(Exception):
    pass
