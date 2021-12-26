import unittest
from textwrap import dedent
from ctrace.tracefile import Tracefile, TracefileDiff


class TestTracefileDiff(unittest.TestCase):
    def test_str(self):
        tracefile1 = Tracefile('/Tracefile1')
        tracefile2 = Tracefile('/Tracefile2')

        tracefile1.arch = 'x86_64'
        tracefile2.arch = 'aarch64'
        tracefile1.add(syscalls={'open', 'write'})
        tracefile2.add(syscalls={'open', 'read'})

        diff = TracefileDiff(tracefile1, tracefile2)
        self.assertEqual(str(diff), dedent('''\
            ARCH
            -x86_64
            +aarch64
            
            SYSCALLS
            -write
            +read'''))
