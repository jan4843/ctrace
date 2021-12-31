import json
import os
import shlex
from ctrace.tracefile import Tracefile


def expand_paths(paths: list[str]) -> list[str]:
    result = []
    for path in paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for name in files:
                    if name[0] != '.':
                        result.append(os.path.join(root, name))
        else:
            result.append(path)
    return result


def cap_options(capabilities: set[str]) -> list[str]:
    options = ['--cap-drop=ALL']
    for cap in sorted(list(capabilities)):
        options.append(f'--cap-add={cap.upper()}')
    return options


def seccomp_options(profile_path: str, syscalls: set[str]) -> list[str]:
    profile = {
        'defaultAction': 'SCMP_ACT_ERRNO',
        'syscalls': [{
            'action': 'SCMP_ACT_ALLOW',
            'names': sorted(list(syscalls))
        }]
    }
    with open(profile_path, 'w', encoding='ascii') as f:
        json.dump(profile, f, indent=4)
        f.write('\n')
    return ['--security-opt=seccomp:' + shlex.quote(profile_path)]


def main(output: str, paths: list[str]):
    tracefiles = expand_paths(paths)
    if not tracefiles:
        print('No Tracefile found')
        return os.EX_NOINPUT

    capabilities = set()
    syscalls = set()
    for tracefile in tracefiles:
        tracefile = Tracefile(tracefile)
        capabilities.update(tracefile.capabilities)
        syscalls.update(tracefile.syscalls)

    options = [
        *cap_options(capabilities),
        *seccomp_options(output, syscalls)
    ]
    print(*options)

    return os.EX_OK
