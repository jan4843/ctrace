from dataclasses import dataclass
from docker import DockerClient
from docker.models.containers import Container
from enum import Enum
from datetime import datetime, timedelta


class ContainerStatus(Enum):
    STARTED = 1
    STOPPED = 2


@dataclass
class ContainerEvent:
    status: ContainerStatus
    container_id: str
    labels: dict[str, str]


class DockerDaemon:
    def __init__(self):
        self.client = DockerClient()

    def events(self, since: datetime = None, until: datetime = None):
        if since is None:
            since = datetime.now()
            for container in self.client.containers.list():
                event = self._parse_container(container)
                if event:
                    yield event

        if until:
            until += timedelta(seconds=1)

        for event in self.client.events(decode=True, since=since, until=until):
            event = self._parse_event(event)
            if event:
                yield event

    def _parse_container(self, container: Container):
        return ContainerEvent(
            status=ContainerStatus.STARTED,
            container_id=container.id,
            labels=self._labels(container.labels)
        )

    def _parse_event(self, event: dict) -> ContainerEvent:
        if event['Type'] != 'container':
            return

        status = self._status(event['status'])
        if not status:
            return

        container_id = event['id']

        labels = self._labels(event['Actor']['Attributes'])

        return ContainerEvent(
            status=status,
            container_id=container_id,
            labels=labels,
        )

    @staticmethod
    def _status(status: str) -> ContainerStatus:
        return {
            'start': ContainerStatus.STARTED,
            'die': ContainerStatus.STOPPED,
        }.get(status)

    @staticmethod
    def _labels(labels: dict[str, str]) -> dict[str, str]:
        return {
            k: v
            for k, v in labels.items()
            if '.' in k
        }
