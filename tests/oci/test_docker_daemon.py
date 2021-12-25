import unittest
from ctrace.oci import docker_daemon, ContainerEvent, ContainerStatus
from datetime import datetime
from utils.docker_run import DockerRun


class TestDockerDaemon(unittest.TestCase):
    def test_get_started_event(self):
        labels = {'com.example.foo': 'bar'}
        time_before = datetime.now()
        with DockerRun('busybox', ['ls'], labels=labels) as container:
            container.wait()
        time_after = datetime.now()

        for event in docker_daemon.events(since=time_before, until=time_after):
            if event.container_id == container.id:
                found_event = event
                break
        if not found_event:
            self.fail('Event not found')

        expected_event = ContainerEvent(
            status=ContainerStatus.STARTED,
            container_id=container.id,
            labels=labels,
        )
        self.assertEqual(found_event, expected_event)

    def test_get_stopped_event(self):
        labels = {'com.example.foo': 'bar'}
        time_before = datetime.now()
        with DockerRun('busybox', ['ls'], labels=labels) as container:
            container.wait()
        time_after = datetime.now()

        for event in docker_daemon.events(since=time_before, until=time_after):
            if event.container_id == container.id:
                found_event = event
        if not found_event:
            self.fail('Event not found')

        expected_event = ContainerEvent(
            status=ContainerStatus.STOPPED,
            container_id=container.id,
            labels=labels,
        )
        self.assertEqual(found_event, expected_event)

    def test_get_running_container_started_event(self):
        labels = {'com.example.foo': 'bar'}
        with DockerRun('busybox', ['sleep', 'infinity'], labels=labels) as container:
            for event in docker_daemon.events():
                if event.container_id == container.id:
                    found_event = event
                    break

        expected_event = ContainerEvent(
            status=ContainerStatus.STARTED,
            container_id=container.id,
            labels=labels,
        )
        self.assertEqual(found_event, expected_event)
