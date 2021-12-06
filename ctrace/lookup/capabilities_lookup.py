import os
from .lookup import Lookup


class CapabilitiesLookup(Lookup):
    _LINUX_RELEASE = os.uname().release
    _KERNEL_SRC = f'/usr/src/linux-headers-{_LINUX_RELEASE}'
    _CAPABILITIES_SRC = f'{_KERNEL_SRC}/include/uapi/linux/capability.h'

    def __init__(self):
        Lookup.__init__(self)
        for line in self._capabilities_src_lines:
            if line.startswith('#define CAP_'):
                definition = line.split()
                try:
                    id_ = int(definition[2])
                    name = definition[1]
                    self._add(id_, name)
                except (KeyError, ValueError):
                    continue

    @property
    def _capabilities_src_lines(self):
        with open(self._CAPABILITIES_SRC, 'r', encoding='ascii') as src:
            return src.readlines()

    def _normalize_name(self, name: str):
        if isinstance(name, bytes):
            name = name.decode()
        name = name.lower()
        if name.startswith('cap_'):
            name = name[len('cap_'):]
        return name
