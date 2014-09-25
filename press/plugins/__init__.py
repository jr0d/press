import imp
import logging
import os

from press.configuration import global_defaults

LOG = logging.getLogger('press.plugins')


def get_plugin(plugin_name, plugin_dir=None):
    if not plugin_dir:
        plugin_dir = global_defaults.plugin_dir
    if not os.path.isdir(plugin_dir):
        LOG.warn('Plugin directory is missing, or relative path is incorrect.'
                 'See press.configuration.global_defaults')
        return

    LOG.debug('Attempting to discover plugin: %s' % plugin_name)

    try:
        mod_info = imp.find_module(plugin_name,
                                   [os.path.join(plugin_dir, plugin_name)])
    except ImportError:
        LOG.error('Plugin %s module does not exist.' % plugin_name)
        return

    mod = imp.load_module(plugin_name, *mod_info)
    if not hasattr(mod, 'plugin_init'):
        LOG.error('Plugin found but is missing init')
        return

    LOG.info('%s plugin module discovered' % plugin_name)
    return mod


def init_plugins(configuration, plugin_dir=None):
    plugins = configuration.get('plugins')
    if not plugins:
        return

    for plugin in plugins:
        mod = get_plugin(plugin, plugin_dir)
        if not mod:
            continue

        LOG.info('Attempting to initialize %s plugin' % plugin)
        try:
            mod.plugin_init(configuration)
        except Exception as e:
            LOG.error('Error running %s plugin init: %s' % (plugin, e))

        LOG.info('%s plugin successfully initialized' % plugin)