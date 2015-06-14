from press.helpers import cli
from press.targets.target_base import TargetExtension

def get_manufacturer():
    res = cli.run('dmidecode -s system-manufacturer', raise_exception=True)

    for line in res.splitlines():
        if line.lstrip().startswith('#'):
            continue
        return line.strip()

class OMSAUbuntu(TargetExtension):
    __extends__ = 'ubuntu_1404'
    pass

