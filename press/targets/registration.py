from __future__ import absolute_import
import collections
import imp
import logging
import os

from press import exceptions

log = logging.getLogger(__name__)


class PostConfigurators(object):
    """
    Configurators now... There has to be a better name for this
    """
    def __init__(self):
        self.vendor = collections.OrderedDict()
        self.extensions = collections.OrderedDict()
        self.overrides = collections.OrderedDict()

post_configurators = PostConfigurators()


def register_vendor_configurators(vendor_path):
    for path, dirs, files in os.walk(vendor_path):
        for _file in files:
            if _file.endswith('_target.py'):
                module_name = os.path.splitext(_file)[0]
                mod_info = imp.find_module(module_name, [path])
                mod = imp.load_module(module_name, *mod_info)
                for k, v in vars(mod).items():
                    # If it looks like a duck
                    if 'Target' in k:
                        name = vars(v).get('name')
                        # And quacks like a duck
                        if name and hasattr(v, 'run'):
                            # This is why we can't have nice things
                            if name not in post_configurators.vendor:
                                log.info('Registering post handler: %s' % v.__name__)
                                post_configurators.vendor[name] = v


def register_extension(cls, run_method='run'):
    if not hasattr(cls, '__extends__'):
        raise exceptions.PressCriticalException('__extends__ attribute is missing')
    if not hasattr(cls, run_method):
        raise exceptions.PressCriticalException('Run method is missing from class')
    log.info('Extending %s target using %s' % (cls.__extends__, cls.__name__))
    post_configurators.extensions[cls.__extends__] = cls


def apply_extension(extension_cls, target_object):
    for mro in target_object.__class__.__mro__:
        if vars(mro).get('name') == extension_cls.__extends__:
            return True
    return False
