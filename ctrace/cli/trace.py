import os
from ctrace.monitor import ContainerMonitor
from ctrace.oci import docker_daemon, ContainerStatus
from ctrace.tracefile import Tracefile
from ctrace.tracer import BPFModule


LABEL = 'ctrace.output-file'

def main(debug=False):
    tracefiles = {}

    with BPFModule(debug=debug) as module:
        monitor = ContainerMonitor(bpf_module=module)

        for event in docker_daemon.events():
            monitor.update()

            if LABEL in event.labels:
                tracefiles[event.container_id] = event.labels[LABEL]
                if event.status == ContainerStatus.STARTED:
                    print('New container', event.container_id)

            for container_id, tracefile in tracefiles.items():
                with Tracefile(tracefile) as tracefile:
                    tracefile.add(
                        capabilities=monitor.last_capabilities(container_id),
                        syscalls=monitor.last_syscalls(container_id),
                    )

            if event.status == ContainerStatus.STOPPED:
                try:
                    del tracefiles[event.container_id]
                except KeyError:
                    pass

    return os.EX_OK
