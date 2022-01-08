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


def noop_executable_path() -> str:
    arch = os.uname().machine
    src_root = pathlib.Path(__file__).parent.parent.as_posix()
    return os.path.join(src_root, 'noop', arch)


def runc_syscalls() -> set():
    with BPFModule(trace_runc=True) as module:
        container = run_noop_container()
        syscalls_counts = module.syscalls_counts(container.id)
        return set(syscalls_counts.keys())


def main(output: str):
    required_syscalls = runc_syscalls()
    count = len(required_syscalls)
    print(f'Found {count} required syscalls for runc')

    with Tracefile(output) as tracefile:
        tracefile.add(syscalls=required_syscalls)

    return os.EX_OK
