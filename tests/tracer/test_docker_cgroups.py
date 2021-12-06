import unittest
from utils.docker_run import DockerRun
from utils import processes
from ctrace.tracer import docker_cgroups


class TestDockerCgroups(unittest.TestCase):
    def test_container_ids(self):
        with DockerRun('busybox', 'sleep infinity') as container:
            self.assertIn(container.id, docker_cgroups.containers_pids.keys())

    def test_container_ids_removal(self):
        with DockerRun('busybox', 'sleep infinity') as container:
            pass
        self.assertNotIn(container.id, docker_cgroups.containers_pids.keys())

    def test_containers_pids(self):
        with DockerRun('busybox', 'sleep infinity') as container:
            container_pids = docker_cgroups.containers_pids[container.id]
            container_pid = container_pids[0]
            container_command = processes.get_pid_command(container_pid)
            self.assertEqual(container_command, ['sleep', 'infinity'])
