import logging

from press.structure import (
    Layout,
    Disk,
    PartitionTable,
    Partition,
)

from press.structure.exceptions import (
    GeneratorError
)

from press.structure.lvm import (
    PhysicalVolume,
    VolumeGroup,
    LogicalVolume
)

from press.structure.filesystems.extended import (
    EXT3,
    EXT4
)

from press.structure.filesystems.swap import (
    SWAP
)

from press.models.lvm import VolumeGroupModel
from press.models.partition import PartitionTableModel


LOG = logging.getLogger(__name__)

MBR_LOGICAL_MAX = 128

_layout_defaults = dict(
    # TODO: Possibly load these from a yaml, defaults.yaml
    use_fibre_channel=False,
    loop_only=False,
    parted_path='parted'
)

_partition_table_defaults = dict(
    # TODO: Alignment will be calculated by the orchestrator using sysfs
    partition_start=1048576,
    alignment=1048576
)

_partition_defaults = dict(
    options=list()
)

_fs_selector = dict(
    ext3=EXT3,
    ext4=EXT4,
    swap=SWAP
)


def index_by_gpt_name():
    pass


def primary_or_logical():
    pass


def _fill_defaults(d, defaults):
    for k in defaults:
        if k not in d:
            d[k] = defaults[k]


def _primary_or_logical(p):
    if 'primary' in p['options']:
        return 'primary'
    if 'logical' in p['options']:
        return 'logical'


def _has_logical(partitions):
    for partition in partitions:
        if _primary_or_logical(partition) == 'logical':
            return True
    return False


def _max_primary(partitions):
    if _has_logical(partitions):
        return 3
    return 4


def generate_partition(type_or_name, partition_dict):
    pass


def _generate_mbr_partitions(partition_dicts):
    """
    MBR:

    There can be four primary partitions unless a logical partition is explicitly
    defined, in such case, there can be only three primary partitions, leaving room
    for an extended partition

    If there are more than four partitions defined and neither primary or logical
    is explicitly defined, then there will be three primary, one extended, and up to 128
    logical partitions.
    """
    max_primary = _max_primary(partition_dicts)

    primary_count = 0
    logical_count = 0

    partitions = list()

    for partition in partition_dicts:
        explicit_name = _primary_or_logical(partition)
        if explicit_name:
            if explicit_name == 'primary':
                if primary_count >= max_primary:
                    raise GeneratorError('Maximum primary partitions have been exceeded')
                primary_count += 1
            elif explicit_name == 'logical':
                if logical_count > MBR_LOGICAL_MAX:
                    raise GeneratorError('Maximum logical partitions have been exceeded')
                logical_count += 1

            partition_type = explicit_name
        else:
            if primary_count < max_primary:
                partition_type = 'primary'
                primary_count += 1
            else:
                if logical_count > MBR_LOGICAL_MAX:
                    raise GeneratorError('Maximum logical partitions have been exceeded')
                partition_type = 'logical'
                logical_count += 1
        partitions.append(generate_partition(partition_type, partition))
    return partitions


def generate_partitions(table_type, partition_dicts):
    for p in partition_dicts:
        _fill_defaults(p, _partition_defaults)

    if table_type == 'msdos':
        return _generate_mbr_partitions(partition_dicts)
    if table_type == 'gpt':
        pass
    else:
        raise GeneratorError('Table type is invalid: %s' % table_type)


def generate_partition_table_model(partition_table_dict):
    """
    Generate a PartitionTableModel, a PartitionTable without a disk association

    Note: if label is not specified, the Press object will determine label based off:
        1. Device booted in UEFI mode
        2. A disk is larger then 2.2TiB

    The press object will also make some decisions based

    Most people don't care if their partitions are primary/logical
    or what their gpt names are, so we'll care for them.


    GPT:

    Use the name field in the configuration or p + count



    :param partition_table_dict:
    :return: PartitionTableModel
    """
    _fill_defaults(partition_table_dict, _partition_table_defaults)
    table_type = partition_table_dict['label']
    pm = PartitionTableModel(
        table_type=partition_table_dict['label'],
        disk=partition_table_dict['disk'],
        partition_start=partition_table_dict['partition_start'],
        alignment=partition_table_dict['alignment']
    )

    partitions = partition_table_dict['partitions']
    if partitions:
        partition_objects = list()
        pass

    return pm


def layout_from_config(layout_config):
    LOG.info('Generating Layout')
    _fill_defaults(layout_config, _layout_defaults)
    layout = Layout(
        use_fibre_channel=layout_config['use_fibre_channel'],
        loop_only=layout_config['loop_only'],
        parted_path=layout_config['parted_path'],
    )

