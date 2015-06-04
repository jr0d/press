from pprint import pprint
import collections
import imp
import os


class PostConfigurators(object):
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
                    if 'Target' in k:
                        name = vars(v).get('name')
                        if name and hasattr(v, 'run'):
                            post_configurators.vendor[name] = v


def register_extension(cls, run_method='run'):
    pass

if __name__ == '__main__':
    register_vendor_configurators('press/targets')
    pprint(post_configurators.vendor)