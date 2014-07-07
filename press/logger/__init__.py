import os
import logging.config

import yaml


def setup_logging(
    default_path='configuration/logging.yaml',
    default_level=logging.DEBUG,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    :param default_path: Path to logging configuration.
    :type default_path: str.

    :param default_level: logging level.
    :type default_level: int.

    :param env_key: Environment key for logger.
    :type env_key: str.

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
