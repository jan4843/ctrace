import unittest
from ctrace.tracer import BPFModule
from utils.docker_run import DockerRun
from utils.processes import get_pid_command


class TestBPFModule(unittest.TestCase):
    def test_pid_to_container(self):
        with BPFModule() as module:
            with DockerRun('busybox', ['sleep', '8393']) as container:
                self.assertIn(container.id, module.pid_to_container.values())

    def test_pid_to_container_removal(self):
        with BPFModule() as module:
            with DockerRun('busybox', ['sleep', '4827']) as container:
                pass
            self.assertNotIn(container.id, module.pid_to_container.values())

    def test_prefill_pid_to_container(self):
        with DockerRun('busybox', ['sleep', '3821']) as container:
            with BPFModule() as module:
                container.exec_run(['date'])
                self.assertIn(container.id, module.pid_to_container.values())

    def test_cgroup_attach_task(self):
        with BPFModule() as module:
            with DockerRun('busybox', ['sleep', '9382']) as container:
                self.assertIn(container.id, module.pid_to_container.values())

    def test_sched_process_exit(self):
        with BPFModule() as module:
            with DockerRun('busybox', ['sleep', '8421']) as container:
                pass
            self.assertNotIn(container.id, module.pid_to_container.values())

    def test_sched_process_fork(self):
        child_command = ['sleep', '4921']
        shell_command = ' '.join(child_command)
        with BPFModule() as module:
            with DockerRun('busybox', ['sh', '-c', shell_command]) as container:
                for pid, container_id in module.pid_to_container.items():
                    if container_id == container.id:
                        if get_pid_command(pid) == child_command:
                            return
                self.fail('PID not found')

    def test_capabilities_counts(self):
        command = ['ping', '-c1', '127.0.0.1']
        expected_capability = 'net_raw'
        with BPFModule() as module:
            with DockerRun('busybox', command) as container:
                pass
            counts = module.capabilities_counts(container.id)
            found_capability_count = counts[expected_capability]
            self.assertGreaterEqual(found_capability_count, 1)

    def test_syscalls_counts(self):
        command = ['date']
        expected_syscall = 'gettimeofday'
        with BPFModule() as module:
            with DockerRun('busybox', command) as container:
                pass
            counts = module.syscalls_counts(container.id)
            found_syscall_count = counts[expected_syscall]
            self.assertGreaterEqual(found_syscall_count, 1)
