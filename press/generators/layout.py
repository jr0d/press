import logging

from press.structure import (
    Layout,
    Partition,
)

from press.structure.exceptions import (
    GeneratorError
)

from press.structure.lvm import (
    PhysicalVolume,
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

__pv_linker__ = dict()

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
    options=list(),
    fsck_option=0
)

_lv_defaults = dict(
    fsck_option=0
)

_fs_selector = dict(
    ext3=EXT3,
    ext4=EXT4,
    swap=SWAP
)

_volume_group_defaults = dict(
    pe_size='4MiB'
)


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


def generate_file_system(fs_dict):
    fs_type = fs_dict.get('type', 'undefined')

    fs_class = _fs_selector.get(fs_type)
    if not fs_class:
        raise GeneratorError('%s type is not supported!' % fs_type)

    fs_object = fs_class(**fs_dict)

    return fs_object


def generate_partition(type_or_name, partition_dict):
    boot = partition_dict['options'].get('boot', False)
    lvm = partition_dict['options'].get('lvm', False)

    fs_dict = partition_dict.get('file_system')

    if fs_dict:
        fs_object = generate_file_system(fs_dict)
        LOG.info('Adding %s file system' % fs_object)
    else:
        fs_object = None

    p = Partition(
        type_or_name=type_or_name,
        size_or_percent=partition_dict['size'],
        boot=boot,
        lvm=lvm,
        file_system=fs_object,
        mount_point=partition_dict.get('mount_point'),
        fsck_option=partition_dict.get('fsck_option')
    )

    if p.lvm:
        # We need to preserve this mapping for generating volume groups
        __pv_linker__[partition_dict['name']] = p

    return p


def _generate_mbr_partitions(partition_dicts):
    """
    There can be four primary partitions unless a logical partition is explicitly
    defined, in such cases, there can be only three primary partitions.

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


def _generate_gpt_partitions(partition_dicts):
    """
    Use the name field in the configuration or p + count
    :param partition_dicts:
    :return: list of Partition objects
    """
    count = 0
    partitions = list()
    for partition in partition_dicts:
        partitions.append(generate_partition(partition.get('name', 'p' + str(count)), partition))
        count += 1
    return partitions


def generate_partitions(table_type, partition_dicts):
    for p in partition_dicts:
        _fill_defaults(p, _partition_defaults)
    if table_type == 'msdos':
        return _generate_mbr_partitions(partition_dicts)
    if table_type == 'gpt':
        return _generate_gpt_partitions(partition_dicts)
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

    :param partition_table_dict:
    :return: PartitionTableModel
    """
    _fill_defaults(partition_table_dict, _partition_table_defaults)
    table_type = partition_table_dict['label']
    pm = PartitionTableModel(
        table_type=table_type,
        disk=partition_table_dict['disk'],
        partition_start=partition_table_dict['partition_start'],
        alignment=partition_table_dict['alignment']
    )

    partition_dicts = partition_table_dict['partitions']
    if partition_dicts:
        partitions = generate_partitions(table_type, partition_dicts)
        pm.add_partitions(partitions)
    return pm


def generate_volume_group_models(volume_group_dict):
    """
    We use __pv_linker__ to reference partition objects by name
    :param volume_group_dict:
    :return:
    """
    if not __pv_linker__:
        raise GeneratorError('__pv_linker__ is null, need to generate Partitions first')
    vgs = list()
    for vg in volume_group_dict:
        _fill_defaults(vg, _volume_group_defaults)
        pvs = list()
        if not vg.get('physical_volumes'):
            raise GeneratorError('No physical volumes are defined')
        for pv in vg.get('physical_volumes'):
            ref = __pv_linker__.get(pv)
            if not ref:
                raise GeneratorError('invalid ref: %s' % pv)
            pvs.append(PhysicalVolume(__pv_linker__[ref]))
        vgm = VolumeGroupModel(vg['name'], pvs)
        lv_dicts = vg.get('logical_volumes')
        lvs = list()
        if lv_dicts:
            for lv in lv_dicts:
                _fill_defaults(lv, _lv_defaults)
                if lv.get('file_system'):
                    fs = generate_file_system(lv.get('file_system'))
                else:
                    fs = None
                lvs.append(LogicalVolume(
                    name=lv['Name'],
                    size_or_percent=lv['size'],
                    file_system=fs,
                    mount_point=lv.get('mount_point'),
                    fsck_option=lv.get('fsck_option')
                ))
            vgm.add_logical_volumes(lvs)
        vgs.append(vg)
    return vgs


def layout_from_config(layout_config):
    LOG.info('Generating Layout')
    _fill_defaults(layout_config, _layout_defaults)
    layout = Layout(
        use_fibre_channel=layout_config['use_fibre_channel'],
        loop_only=layout_config['loop_only'],
        parted_path=layout_config['parted_path'],
    )

    partition_tables = layout_config.get('partition_tables')
    if not partition_tables:
        raise GeneratorError('No partition tables have been defined')

    for pt in partition_tables:
        ptm = generate_partition_table_model(pt)
        layout.add_partition_table_from_model(ptm)

    volume_groups = layout_config.get('volume_groups')
    if volume_groups:
        vg_objects = generate_volume_group_models(volume_groups)

        for vg in vg_objects:
            layout.add_volume_group_from_model(vg)

