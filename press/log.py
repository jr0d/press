import logging
import yaml

from press.configuration.util import environment_cache


FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def setup_logging():
    env_logging = environment_cache.get('logging')
    logging.basicConfig(format=FORMAT)

    press_logger = logging.getLogger('press')
    press_cli_logger = logging.getLogger('press.helpers.cli')

    if env_logging.get('console_enabled', True):  # True unless explicitly defined
        stream_handler = logging.StreamHandler()
        press_logger.addHandler(stream_handler)
        press_logger.setLevel(logging.getLevelName(env_logging.get('level', 'INFO')))

    log_path = env_logging.get('log_path')

    if log_path:
        press_logger.info('Setting log file: {}'.format(log_path))
        press_logger.addHandler(logging.FileHandler(log_path))

    if not env_logging.get('cli_logging_enabled'):
        press_cli_logger.setLevel(logging.ERROR)  # Only log on error
