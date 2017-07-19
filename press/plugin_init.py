# TODO: re-implement with importlib
from __future__ import absolute_import

import imp
import logging
import os

from press.configuration.util import environment_cache

LOG = logging.getLogger('press.plugins')


def get_plugin(plugin_name):

    plugin_dirs = environment_cache.get('plugins', {}).get('scan_directories')
    if not plugin_dirs:
        LOG.warn('There are no plugin.scan_directories defined')
        return

    mod_info = None
    for d in plugin_dirs:
        if not os.path.isdir(d):
            LOG.warn('Plugin directory {} is missing, or relative path is incorrect.'
                     'See press.configuration.global_defaults'.format(d))
            continue

        LOG.debug('Attempting to discover plugin: %s' % plugin_name)

        try:
            mod_info = imp.find_module(plugin_name,
                                       [os.path.join(d, plugin_name)])
        except ImportError:
            LOG.debug('Plugin %s module does not exist.' % plugin_name)
            continue

    if not mod_info:
        LOG.error('plugin "{}" could not be found in any search directory. Skipping'.format(plugin_name))
        return

    mod = imp.load_module(plugin_name, *mod_info)

    if not hasattr(mod, 'plugin_init'):
        LOG.error('Plugin {} found but is missing init'.format(plugin_name))
        return

    LOG.info('%s plugin module discovered' % plugin_name)
    return mod


def init_plugins(configuration):
    plugins = environment_cache.get('plugins', {}).get('enabled')

    if not plugins:
        LOG.debug('No plugins are enabled')
        return

    for plugin in plugins:
        mod = get_plugin(plugin)
        if not mod:
            continue

        LOG.info('Attempting to initialize %s plugin' % plugin)
        try:
            mod.plugin_init(configuration)
        except Exception as e:
            LOG.error('Error running %s plugin init: %s' % (plugin, e))

        LOG.info('%s plugin successfully initialized' % plugin)
