import logging

from press.structure import Size


class VolumeGroupModel(object):
    def __init__(self, name, partition_refs, pe_size='4MiB'):
        self.logical_volumes = list()

        self.name = name
        self.partition_refs = partition_refs
        self.pe_size = Size(pe_size)

    def add_logical_volume(self, lv):
        self.logical_volumes.append(lv)