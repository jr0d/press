from decimal import Decimal, InvalidOperation


class SizeObjectValError(Exception):
    pass


class Size(object):
    byte = 1
    kibibyte = 1024
    mebibyte = kibibyte ** 2
    gibibyte = kibibyte ** 3
    tebibyte = kibibyte ** 4
    pebibyte = kibibyte ** 5
    exbibyte = kibibyte ** 6
    zebibyte = kibibyte ** 7
    yobibyte = kibibyte ** 8

    # Because we are dealing with disks, we'll probably need decimal byte notation

    kilobyte = 1000
    megabyte = kilobyte ** 2
    gigabyte = kilobyte ** 3
    terabyte = kilobyte ** 4
    petabyte = kilobyte ** 5
    exabyte = kilobyte ** 6
    zettabyte = kilobyte ** 7
    yottabyte = kilobyte ** 8

    sector = 512

    symbols = {
        'b': byte,
        'k': kilobyte,
        'kB': kilobyte,
        'KiB': kibibyte,
        'M': megabyte,
        'MB': megabyte,
        'MiB': mebibyte,
        'G': gigabyte,
        'GB': gigabyte,
        'GiB': gibibyte,
        'T': terabyte,
        'TB': terabyte,
        'TiB': tebibyte,
        'PB': petabyte,
        'PiB': pebibyte,
        'EB': exabyte,
        'EiB': exbibyte,
        'YB': yottabyte,
        'YiB': yobibyte,
        's': sector
    }

    def __init__(self, value):
        self.bytes = self._convert(value)

    def _convert(self, value):
        if isinstance(value, (int, long)):
            if value > self.yobibyte:
                raise SizeObjectValError('Value is impossibly large.')
            return value

        if isinstance(value, (float, Decimal)):
            return int(round(value))

        if not isinstance(value, (str, unicode)):
            raise SizeObjectValError(
                'Value is not in a format I can understand')

        if value.isdigit():
            return int(value)

        valid_suffices = self.symbols.keys()
        suffix_index = 0
        for valid_suffix in valid_suffices:
            our_index = value.find(valid_suffix)
            if our_index and our_index != -1:
                suffix_index = our_index
                break
        if not suffix_index:
            raise SizeObjectValError(
                'Value is not in a format I can understand. Invalid Suffix.')

        val, suffix = value[:suffix_index].strip(), value[suffix_index:].strip()

        if suffix not in valid_suffices:
            raise SizeObjectValError(
                'Value is not in a format I can understand. Invalid Suffix.')

        try:
            val = Decimal(val)
        except InvalidOperation:
            raise SizeObjectValError(
                'Value is not in a format I can understand. '
                'Could not convert value to int')

        return int(round(val * self.symbols[suffix]))

    @property
    def humanize(self):
        units = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'TiB']
        if self.bytes < self.symbols['KiB']:
            return '%d b' % self.bytes

        for idx in range(1, len(units)):
            if self.bytes < self.symbols[units[idx]]:
                unit = units[idx - 1]
                return '%s %s' % (Decimal(self.bytes) / self.symbols[unit], unit)

        raise SizeObjectValError('Something very strange has happened.')

    @property
    def megabytes(self):
        return Decimal(self.bytes) / self.megabyte

    def __repr__(self):
        rep = '<%s> : %ib' % (self.__class__.__name__, self.bytes)
        return rep

    def __str__(self):
        return str(self.humanize)

    def __unicode__(self):
        return self.humanize

    def __add__(self, other):
        return Size(self.bytes + other.bytes)

    def __sub__(self, other):
        return Size(self.bytes - other.bytes)

    def __mul__(self, other):
        return Size(self.bytes * other.bytes)

    def __div__(self, other):
        'dont devide by zero.'
        return Size(other.bytes / self.bytes)

    def __lt__(self, other):
        return self.bytes < other.bytes

    def __le__(self, other):
        return self.bytes <= other.bytes

    def __eq__(self, other):
        return self.bytes == other.bytes

    def __ne__(self, other):
        return self.bytes <> other.bytes

    def __gt__(self, other):
        return self.bytes > other.bytes

    def __ge__(self, other):
        return self.bytes >= other.bytes

    def __truedev__(self, other):
        'dont device by zero'
        return Size(other.bytes / self.bytes)
