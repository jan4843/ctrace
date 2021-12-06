from .syscalls_lookup import SyscallsLookup
from .capabilities_lookup import CapabilitiesLookup


__all__ = [
    'capabilities',
    'syscalls',
]

capabilities = CapabilitiesLookup()
syscalls = SyscallsLookup()
