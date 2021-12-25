import unittest
from utils.docker_run import DockerRun
from ctrace.tracer import BPFModule
from ctrace.monitor import ContainerMonitor


class TestContainerMonitor(unittest.TestCase):
    def test_last_capabilities(self):
        command = ['ping', '-c1', '127.0.0.1']
        expected_capability = 'net_raw'
        with BPFModule() as module:
            with DockerRun('busybox', ['sleep', '4921']) as container:
                monitor = ContainerMonitor(bpf_module=module)
                container.exec_run(command)
                monitor.update()
        self.assertIn(expected_capability, monitor.last_capabilities(container.id))

    def test_last_syscalls(self):
        command = ['date']
        expected_syscall = 'gettimeofday'
        with BPFModule() as module:
            with DockerRun('busybox', ['sleep', '1232']) as container:
                monitor = ContainerMonitor(bpf_module=module)
                container.exec_run(command)
                monitor.update()
        self.assertIn(expected_syscall, monitor.last_syscalls(container.id))

    def test_update(self):
        with BPFModule() as module:
            monitor = ContainerMonitor(bpf_module=module)
            with DockerRun('busybox', ['sleep', '9372']) as container:
                container.exec_run(['ls'])
                monitor.update()
                monitor.update()
        self.assertEqual(monitor.last_capabilities(container.id), set())
