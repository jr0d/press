import logging
import sys


from .logger import setup_logging
from .plugins import init_plugins
from .press_main import Press
from traceback import format_exception

log = logging.getLogger('press')


def entry_main(configuration, plugin_dir=None):
    setup_logging()
    log.info('Logger initialized')
    init_plugins(configuration, plugin_dir)
    log.info('Plugins initialized')
    try:
        press = Press(configuration)
    except Exception as e:
        traceback = format_exception(*sys.exc_info())
        log.error('Critical Error, %s, during initialization' % e, extra=dict(traceback=traceback,
                                                                              press_event='critical'))
        raise
    try:
        press.run()
    except Exception as e:
        traceback = format_exception(*sys.exc_info())
        log.error('Critical Error, %s, during deployment' % e, extra=dict(traceback=traceback,
                                                                          press_event='critical'))
        raise
    finally:
        if press.layout.committed:
            press.teardown()