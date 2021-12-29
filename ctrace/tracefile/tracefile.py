import os
from pathlib import Path


class Tracefile:
    def __init__(self, path: str):
        self.arch = os.uname().machine
        self.capabilities = set()
        self.syscalls = set()
        self.file = path
        if self.exists:
            self._parse_file()

    def add(self, capabilities: set[str] = set(), syscalls: set[str] = set()) -> None:
        self.capabilities.update(capabilities)
        self.syscalls.update(syscalls)

    def _parse_file(self) -> None:
        with open(self.file, 'r', encoding='ascii') as tracefile:
            lines = [l.strip() for l in tracefile.readlines() if l.strip()]
        section = None
        for line in lines:
            if not line:
                continue
            if line.isupper():
                section = line
                continue

            if section == 'ARCH':
                self.arch = line
            elif section == 'CAPABILITIES':
                self.capabilities.add(line)
            elif section == 'SYSCALLS':
                self.syscalls.add(line)

    @property
    def exists(self):
        return os.path.isfile(self.file)

    def __str__(self):
        return '\n'.join([
            'ARCH', self.arch, '',
            'CAPABILITIES', *sorted(self.capabilities), '',
            'SYSCALLS', *sorted(self.syscalls),
        ])

    def write(self):
        dir_name = os.path.dirname(self.file)
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        with open(self.file, 'w', encoding='ascii') as f:
            f.write(str(self) + '\n')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write()

    def __eq__(self, other):
        if not isinstance(other, Tracefile):
            return False

        return (
            self.arch == other.arch and
            self.capabilities == other.capabilities and
            self.syscalls == other.syscalls
        )
