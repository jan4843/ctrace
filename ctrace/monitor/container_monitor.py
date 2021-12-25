from ctrace.tracer import BPFModule


class ContainerMonitor:
    def __init__(self, bpf_module: BPFModule):
        self._bpf_module = bpf_module
        self._last_containers_capabilities_counts = {}
        self._last_containers_syscalls_counts = {}
        self._last_capabilities = set()
        self._last_syscalls = set()
        self.update()

    def update(self) -> None:
        old_cap = self._last_containers_capabilities_counts
        new_cap = self._current_containers_capabilities_counts
        self._last_capabilities = self._diff(old_cap, new_cap)
        self._last_containers_capabilities_counts = new_cap

        old_sys = self._last_containers_syscalls_counts
        new_sys = self._current_containers_syscalls_counts
        self._last_syscalls = self._diff(old_sys, new_sys)
        self._last_containers_syscalls_counts = new_sys

    def last_capabilities(self, container_id: str) -> set[str]:
        return self._last_capabilities[container_id]

    def last_syscalls(self, container_id: str) -> set[str]:
        return self._last_syscalls[container_id]

    @staticmethod
    def _diff(old: dict[str, dict[str, int]], new: dict[str, dict[str, int]]) -> set[str]:
        result = {}
        for container_id, counts in new.items():
            result[container_id] = set()
            if container_id not in old:
                result[container_id].update(counts.keys())
            else:
                for syscall, count in counts.items():
                    if syscall not in old[container_id]:
                        result[container_id].add(syscall)
                    elif count != old[container_id][syscall]:
                        result[container_id].add(syscall)
        return result

    @property
    def _current_containers_capabilities_counts(self) -> dict[str, dict[str, int]]:
        return self._current_containers_counts(self._bpf_module.capabilities_counts)

    @property
    def _current_containers_syscalls_counts(self) -> dict[str, dict[str, int]]:
        return self._current_containers_counts(self._bpf_module.syscalls_counts)

    def _current_containers_counts(self, get_counts) -> dict[str, dict[str, int]]:
        result = {}
        for container_id in self._bpf_module.container_ids:
            syscall_counts = get_counts(container_id)
            result[container_id] = syscall_counts
        return result
