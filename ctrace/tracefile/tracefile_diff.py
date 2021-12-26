from .tracefile import Tracefile


class TracefileDiff:
    def __init__(self, tracefile1: Tracefile, tracefile2: Tracefile):
        self.tracefile1 = tracefile1
        self.tracefile2 = tracefile2

    def __str__(self):
        sections = []

        if self.tracefile1.arch != self.tracefile2.arch:
            diff = self._set_diff({self.tracefile1.arch}, {self.tracefile2.arch})
            sections.append(['ARCH', *diff])
        if self.tracefile1.capabilities != self.tracefile2.capabilities:
            diff = self._set_diff(self.tracefile1.capabilities, self.tracefile2.capabilities)
            sections.append(['CAPABILITIES', *diff])
        if self.tracefile1.syscalls != self.tracefile2.syscalls:
            diff = self._set_diff(self.tracefile1.syscalls, self.tracefile2.syscalls)
            sections.append(['SYSCALLS', *diff])

        sections = ['\n'.join(section) for section in sections]
        return '\n\n'.join(sections)

    @staticmethod
    def _set_diff(set1: set[str], set2: set[str]) -> list[str]:
        r = [f'-{c}' for c in set1.difference(set2)]
        l = [f'+{c}' for c in set2.difference(set1)]
        return [*sorted(r), *sorted(l)]
