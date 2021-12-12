import unittest
from utils.docker_run import DockerRun
from utils.processes import get_pid_command
from ctrace.tracer import docker_cgroups


class TestDockerCgroups(unittest.TestCase):
    def test_container_ids(self):
        with DockerRun('busybox', ['sleep', 'infinity']) as container:
            self.assertIn(container.id, docker_cgroups.containers_pids.keys())

    def test_container_ids_removal(self):
        with DockerRun('busybox', ['sleep', 'infinity']) as container:
            pass
        self.assertNotIn(container.id, docker_cgroups.containers_pids.keys())

    def test_containers_pids(self):
        init_command = ['sleep', '42']
        with DockerRun('busybox', init_command) as container:
            container_pids = docker_cgroups.containers_pids[container.id]
            init_pid = container_pids[0]
            found_command = get_pid_command(init_pid)
            self.assertEqual(found_command, init_command)
