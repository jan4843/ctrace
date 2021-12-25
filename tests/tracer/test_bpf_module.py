import unittest
from ctrace.tracer import BPFModule
from utils.docker_run import DockerRun
from utils.processes import get_pid_command


class TestBPFModule(unittest.TestCase):
    def test_pid_to_containers_len(self):
        with BPFModule() as module:
            module.pid_to_container[4823] = '4e1de613e001'
            self.assertGreater(len(module.pid_to_container), 0)

    def test_pid_to_containers_get_se(self):
        pid = 5832
        container_id = 'e9eeec521828'
        with BPFModule() as module:
            module.pid_to_container[pid] = container_id
            self.assertEqual(module.pid_to_container[pid], container_id)

    def test_pid_to_containers_inexistent(self):
        with self.assertRaises(KeyError):
            with BPFModule() as module:
                _ = module.pid_to_container[9999]

    def test_pid_to_containers_del(self):
        pid = 3821
        with BPFModule() as module:
            module.pid_to_container[pid] = '62764899b2de'
            del module.pid_to_container[pid]
            with self.assertRaises(KeyError):
                _ = module.pid_to_container[pid]

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
