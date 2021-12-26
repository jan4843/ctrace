import os
from ctrace.tracefile import Tracefile, TracefileDiff


def main(tracefile1, tracefile2):
    tracefile1 = Tracefile(tracefile1)
    tracefile2 = Tracefile(tracefile2)

    if not tracefile1.exists and not tracefile2.exists:
        print('No Tracefile found')
        return os.EX_NOINPUT

    if tracefile1 != tracefile2:
        diff = TracefileDiff(tracefile1, tracefile2)
        print(diff)
        return 1

    return os.EX_OK
