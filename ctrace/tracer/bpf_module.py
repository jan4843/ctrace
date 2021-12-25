import os
from ctypes import c_int
from bcc import BPF
from bcc.table import HashTable
from ctrace.lookup import capabilities, syscalls


class PidToContainerDict:
    def __init__(self, bpf_map: HashTable):
        self._bpf_map = bpf_map

    def _key(self, pid: int):
        return self._bpf_map.Key(pid)

    def _value(self, container_id: str):
        return self._bpf_map.Leaf(id=container_id.encode())

    def __len__(self) -> int:
        return len(self._bpf_map)

    def __getitem__(self, pid: int) -> str:
        key = self._key(pid)
        value = self._bpf_map[key]
        return value.id.decode()

    def __setitem__(self, pid: int, container_id: str) -> None:
        key = self._key(pid)
        value = self._value(container_id)
        self._bpf_map[key] = value

    def __delitem__(self, pid: int) -> None:
        key = self._key(pid)
        del self._bpf_map[key]

    def __iter__(self):
        return self.Iter(self._bpf_map)

    def itervalues(self):
        for key in self:
            yield self[key]

    def iteritems(self):
        for key in self:
            yield (key, self[key])

    def keys(self) -> list[int]:
        return iter(self)

    def values(self) -> list[str]:
        return list(self.itervalues())

    def items(self) -> list[tuple[int, str]]:
        return list(self.iteritems())

    class Iter:
        def __init__(self, bpf_map: HashTable):
            self._iter = iter(bpf_map)

        def __next__(self) -> int:
            key = next(self._iter)
            return key.value


class BPFModule:
    _BPF_SRC_FILENAME = 'module.bpf.c'

    def __init__(self, trace_runc=False, debug=False):
        self._bpf_program = None
        self.trace_runc = trace_runc
        self.debug = debug

    def __enter__(self):
        self._bpf_program = BPF(
            src_file=self._bpf_src_path,
            cflags=self._cflags,
        )
        if self.debug:
            self._prefill_names()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._bpf_program.cleanup()

    @property
    def _bpf_src_path(self):
        directory = os.path.dirname(__file__)
        return os.path.join(directory, self._BPF_SRC_FILENAME)

    @property
    def _cflags(self):
        flags = []
        if self.trace_runc:
            flags.append('-DTRACE_RUNC=1')
        if self.debug:
            flags.append('-DDEBUG=1')
            return ['-DDEBUG=1']
        return flags

    @property
    def pid_to_container(self):
        bpf_map = self._bpf_program['pid_to_container']
        return PidToContainerDict(bpf_map)

    def capabilities_counts(self, container_id: str) -> dict[str, int]:
        return self._counts(
            bpf_map='container_capability_count',
            container_id=container_id,
            transform_key=lambda id_: capabilities.names[id_],
        )

    def syscalls_counts(self, container_id: str) -> dict[str, int]:
        return self._counts(
            bpf_map='container_syscall_count',
            container_id=container_id,
            transform_key=lambda id_: syscalls.names[id_],
        )

    def _counts(self, bpf_map, container_id, transform_key) -> dict[str, int]:
        result = {}
        for key, value in self._bpf_program[bpf_map].items():
            item_container_id = key.container.id.decode()
            if item_container_id == container_id:
                item_key = key.key
                item_value = value.value
                result[transform_key(item_key)] = item_value
        return result

    def _prefill_names(self):
        cap = ('capability_names', capabilities)
        sys = ('syscall_names', syscalls)
        for bpf_map, lookup in [cap, sys]:
            bpf_map = self._bpf_program[bpf_map]
            string_struct = bpf_map.Leaf
            for id_, name in lookup.names.items():
                key = c_int(id_)
                value = string_struct(value=name.encode())
                bpf_map[key] = value
