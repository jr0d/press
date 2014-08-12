import logging

from press.structure import (
    Layout,
    Disk,
    PartitionTable,
    Partition
)

from press.structure.lvm import (
    PhysicalVolume,
    VolumeGroup,
    LogicalVolume
)

from press.structure.exceptions import (
    PhysicalDiskException,
    LayoutValidationError,
    GeneralValidationException
)

from press.models.lvm import VolumeGroupModel
from press.models.partition import PartitionTableModel


LOG = logging.getLogger(__name__)


_layout_defaults = dict(
    use_fibre_channel=False,
    loop_only=False,
    default_partition_start=1048576,
    default_alignment=1048576,
    disk_association='explicit',
    parted_path='parted'
)

_partition_table_defaults = dict(
    label='msdos'
)


def _fill_defaults(d, defaults):
    for k in defaults:
        if k not in d:
            d[k] = defaults[k]


def layout_from_config(layout_config):
    LOG.info('Generating Layout')
    _fill_defaults(layout_config, _layout_defaults)
    layout = Layout(
        use_fibre_channel=layout_config['use_fibre_channel'],
        loop_only=layout_config['loop_only'],
        parted_path=layout_config['parted_path'],
        default_partition_start=layout_config['default_partition_start'],
        default_alignment=layout_config['default_alignment'],
        disk_association=layout_config['disk_association']
    )
