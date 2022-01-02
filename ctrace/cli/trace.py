import os
import queue
import threading
from ctrace.monitor import ContainerMonitor
from ctrace.oci import docker_daemon, ContainerStatus
from ctrace.tracefile import Tracefile
from ctrace.tracer import BPFModule

LABEL = 'ctrace.output-file'
TIMEOUT = 15


class TimeoutIterator:
    def __init__(self, timeout, iterator):
        self._timeout = timeout
        self._iterator = iterator

        self._buffer = queue.Queue()
        self._thread = threading.Thread(target=self._iterate, daemon=True)
        self._thread.start()

    def __iter__(self):
        return self

    def __next__(self):
        data = None
        try:
            data = self._buffer.get(timeout=self._timeout)
        except queue.Empty:
            pass
        if isinstance(data, BaseException):
            raise data
        return data

    def _iterate(self):
        try:
            while True:
                self._buffer.put(next(self._iterator))
        except BaseException as e:
            self._buffer.put(e)


def handle_event(event, tracefiles, monitor):
    if event and LABEL in event.labels:
        tracefiles[event.container_id] = event.labels[LABEL]
        print(
            'Started' if event.status == ContainerStatus.STARTED else 'Stopped',
            'container',
            event.container_id,
        )

    for container_id, tracefile in tracefiles.items():
        with Tracefile(tracefile) as tracefile:
            tracefile.add(
                capabilities=monitor.last_capabilities(container_id),
                syscalls=monitor.last_syscalls(container_id),
            )

    if event and event.status == ContainerStatus.STOPPED:
        try:
            del tracefiles[event.container_id]
        except KeyError:
            pass


def main(debug=False, trace_runc=False):
    tracefiles = {}
    event_iterator = TimeoutIterator(TIMEOUT, docker_daemon.events())
    try:
        with BPFModule(debug=debug, trace_runc=trace_runc) as module:
            monitor = ContainerMonitor(bpf_module=module)
            print('Waiting for Docker events')
            for event in event_iterator:
                monitor.update()
                handle_event(event, tracefiles, monitor)
    except KeyboardInterrupt:
        return os.EX_OK
