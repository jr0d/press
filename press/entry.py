import logging
import sys

from traceback import format_exception

# Press Imports
from press.configuration.util import set_environment_from_file, environment_cache
from press.log import setup_logging
from press.plugin_init import init_plugins
from press.press import Press

log = logging.getLogger('press')


def entry_main(
        configuration,
        environment_configuration_path=None,
        initialize_logging=True
):
    set_environment_from_file(environment_configuration_path)

    if initialize_logging:
        setup_logging()
        log.info('Logger initialized')

    init_plugins(configuration)
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
