import docker
import json
import os
import pathlib
from ctrace.tracer import BPFModule
from ctrace.tracefile import Tracefile

docker_client = docker.from_env()


def run_noop_container(**kwargs) -> docker.models.containers.Container:
    docker_client.images.pull('busybox', tag='latest')
    container = docker_client.containers.run(
        'busybox',
        volumes=[noop_executable_path()+':/noop'],
        entrypoint=['/noop'],
        **kwargs,
        remove=True,
        detach=True,
    )
    container.wait()
    return container


def container_can_start_with(syscalls: set[str]) -> bool:
    docker_client.images.pull('busybox', tag='latest')
    try:
        container = run_noop_container(
            security_opt=['seccomp:'+seccomp_profile(syscalls)],
        )
        return container.attrs['State']['ExitCode'] == 0
    except (docker.errors.APIError, KeyError):
        return False


def runc_syscalls() -> set():
    with BPFModule(trace_runc=True) as module:
        container = run_noop_container()
        return set(module.syscalls_counts(container.id).keys())


def seccomp_profile(syscalls: set[str]) -> str:
    return json.dumps({
        'defaultAction': 'SCMP_ACT_ERRNO',
        'syscalls': [{
            'action': 'SCMP_ACT_ALLOW',
            'names': list(syscalls)
        }]
    })


def noop_executable_path():
    arch = os.uname().machine
    src_root = pathlib.Path(__file__).parent.parent.as_posix()
    return os.path.join(src_root, 'noop', arch)


def main(output: str, minimize: bool):
    required_syscalls = sorted(list(runc_syscalls()))
    count = len(required_syscalls)
    print(f'Found {count} potential required syscalls')

    if minimize:
        for index, potential_syscall in enumerate(required_syscalls[:], start=1):
            print(f'({index}/{count}) Testing {potential_syscall}...')
            syscalls_except_current = [s for s in required_syscalls if s != potential_syscall]
            if container_can_start_with(syscalls_except_current):
                required_syscalls.remove(potential_syscall)

    with Tracefile(output) as tracefile:
        tracefile.add(syscalls=required_syscalls)

    return os.EX_OK
