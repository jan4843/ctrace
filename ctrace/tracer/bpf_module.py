import os
from ctypes import c_int
from bcc import BPF
from bcc.table import HashTable
from ctrace.lookup import capabilities, syscalls
from ctrace.oci import docker_cgroups


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
        self._prefill_pid_to_container()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._bpf_program.cleanup()

    @property
    def _bpf_src_path(self) -> str:
        directory = os.path.dirname(__file__)
        return os.path.join(directory, self._BPF_SRC_FILENAME)

    @property
    def _cflags(self) -> list[str]:
        flags = []
        if self.trace_runc:
            flags.append('-DTRACE_RUNC=1')
        if self.debug:
            flags.append('-DDEBUG=1')
            return ['-DDEBUG=1']
        return flags

    @property
    def container_ids(self) -> set[str]:
        result = set()
        for value in self._bpf_program['pid_to_container'].values():
            container_id = value.id.decode()
            result.add(container_id)
        for key in self._bpf_program['container_syscall_count'].keys():
            container_id = key.container.id.decode()
            result.add(container_id)
        return result

    @property
    def pid_to_container(self) -> dict[int, str]:
        bpf_map = self._bpf_program['pid_to_container']
        result = {}
        for key, value in bpf_map.items():
            pid = int(key.value)
            container_id = str(value.id.decode())
            result[pid] = container_id
        return result

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

    def _prefill_names(self) -> None:
        cap = ('capability_names', capabilities)
        sys = ('syscall_names', syscalls)
        for bpf_map, lookup in [cap, sys]:
            bpf_map = self._bpf_program[bpf_map]
            string_struct = bpf_map.Leaf
            for id_, name in lookup.names.items():
                key = c_int(id_)
                value = string_struct(value=name.encode())
                bpf_map[key] = value

    def _prefill_pid_to_container(self) -> None:
        bpf_map = self._bpf_program['pid_to_container']
        for container_id, pids in docker_cgroups.containers_pids.items():
            for pid in pids:
                key = bpf_map.Key(pid)
                value = bpf_map.Leaf(id=container_id.encode())
                bpf_map[key] = value
