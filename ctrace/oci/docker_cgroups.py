import os


class DockerCgroups:
    _CONTAINER_ID_LONG_LEN = 64
    _CONTAINER_ID_SHORT_LEN = 12
    _CGROUP_DIR = '/sys/fs/cgroup/pids/docker'
    _CGROUP_TASKS_PATH = _CGROUP_DIR + '/{container_id}/tasks'

    @property
    def containers_pids(self) -> dict[str, list[int]]:
        mapping = {}
        for container_id in self._container_ids:
            pids = self._container_pids(container_id)
            mapping[container_id] = pids
        return mapping

    @property
    def _container_ids(self) -> list[str]:
        ids = []
        for cgroup in os.scandir(self._CGROUP_DIR):
            name = cgroup.name
            if len(name) == self._CONTAINER_ID_LONG_LEN:
                ids.append(name)
        return ids

    def _container_pids(self, container_id: str) -> list[int]:
        path = self._CGROUP_TASKS_PATH.format(container_id=container_id)
        pids = []
        try:
            with open(path, 'r', encoding='ascii') as tasks:
                for pid in tasks.readlines():
                    pid = int(pid)
                    pids.append(pid)
        except FileNotFoundError:
            pass
        return pids
