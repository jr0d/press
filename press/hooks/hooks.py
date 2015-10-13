from __future__ import absolute_import
import logging
from collections import namedtuple

from press.exceptions import HookError

log = logging.getLogger(__name__)


Hook = namedtuple("Hook", "function args kwargs")

valid_hook_points = ["pre-apply-layout", "pre-mount-fs", "pre-image-ops", "pre-post-config", "pre-create-staging",
                     "pre-target-run", "pre-extensions", "post-extensions"]
target_hooks = {}

for point in valid_hook_points:
    target_hooks[point] = []


def add_hook(func, hook_point, *args, **kwargs):
    log.debug("Adding hook '{0}' for point '{1}'".format(func.__name__, hook_point))
    if hook_point not in valid_hook_points:
        raise HookError("Not a valid hook point '{0}'".format(hook_point))
    target_hooks[hook_point].append(Hook(function=func, args=args, kwargs=kwargs))


def run_hooks(hook_point):
    if hook_point not in valid_hook_points:
        log.warning("Specified hook point '{0}' does not exist".format(hook_point))
        return

    for hook in target_hooks[hook_point]:
        log.debug("Running hook '{0}' for point '{1}'".format(func.__name__, hook_point))
        hook.function(*hook.args, **hook.kwargs)
