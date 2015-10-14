"""
Hooks are to be used to execute sections of code as needed throughout the Press process.
"""


from __future__ import absolute_import
import logging
import inspect
from functools import wraps
from collections import namedtuple

from press.exceptions import HookError

log = logging.getLogger(__name__)


Hook = namedtuple("Hook", "function args kwargs")

valid_hook_points = ["post-press-init", "pre-apply-layout", "pre-mount-fs",
                     "pre-image-ops", "pre-post-config", "pre-create-staging",
                     "pre-target-run", "pre-extensions", "post-extensions"]
target_hooks = {}

for valid_point in valid_hook_points:
    target_hooks[valid_point] = []


def add_hook(func, point, *args, **kwargs):
    """Add a function as a hook, make sure the function accepts a keyword argument 'press_config'"""
    if "press_config" not in inspect.getargspec(func).args:
        raise HookError("Attempted hook function '{0}' does not accept argument 'press_config'".format(func.__name__))

    log.debug("Adding hook '{0}' for point '{1}'".format(func.__name__, point))
    if point not in valid_hook_points:
        raise HookError("Not a valid hook point '{0}'".format(point))
    target_hooks[point].append(Hook(function=func, args=args, kwargs=kwargs))


def run_hooks(point, press_config):

    log.info("Running hooks for point '{0}'".format(point))
    if point not in valid_hook_points:
        log.warning("Specified hook point '{0}' does not exist".format(point))
        return

    for hook in target_hooks[point]:
        log.debug("Running hook '{0}' for point '{1}'".format(hook.function.__name__, point))
        hook.function(*hook.args, press_config=press_config, **hook.kwargs)


def hook_point(point):
    """
    Wrapper for adding a function as a hook,
    make sure the function accepts a keyword argument 'press_config'
    """
    def decorate(func):
        @wraps(func)
        def call(*args, **kwargs):
            add_hook(func, point, *args, **kwargs)
        return call
    return decorate
