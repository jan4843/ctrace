import seccomp
from .lookup import Lookup


class SyscallsLookup(Lookup):
    def __init__(self):
        Lookup.__init__(self)
        for id_ in range(0, 1024):
            try:
                name = seccomp.resolve_syscall(arch=0, syscall=id_)
                self._add(id_, name)
            except ValueError:
                continue

    def _normalize_name(self, name: str):
        if isinstance(name, bytes):
            name = name.decode()
        return name.lower()
