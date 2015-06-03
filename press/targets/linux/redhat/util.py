"""
General utilities for working with RedHat based images
"""

from press.helpers.cli import run_chroot


def get_package_list(rpm_path='/usr/bin/rpm'):
    command = '%s --query --all --queryformat \"\%{NAME}\\n\"'
