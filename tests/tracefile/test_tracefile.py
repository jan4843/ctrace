import unittest
import tempfile
from textwrap import dedent
from ctrace.tracefile import Tracefile


class TestTracefile(unittest.TestCase):
    def test_parse(self):
        with tempfile.NamedTemporaryFile('w') as f:
            f.write(dedent('''\
                ARCH
                x86_64

                CAPABILITIES
                net_admin

                SYSCALLS
                open
                write
            '''))
            f.seek(0)

            tracefile = Tracefile(f.name)
            self.assertEqual(tracefile.arch, 'x86_64')
            self.assertEqual(tracefile.capabilities, {'net_admin'})
            self.assertEqual(tracefile.syscalls, {'open', 'write'})

    def test_add(self):
        capabilities = {'net_raw'}
        syscalls = {'bind', 'read'}
        with tempfile.NamedTemporaryFile('w') as f:
            tracefile = Tracefile(f.name)
            tracefile.add(capabilities=capabilities, syscalls=syscalls)
            self.assertEqual(tracefile.capabilities, capabilities)
            self.assertEqual(tracefile.syscalls, syscalls)

    def test_str(self):
        with tempfile.NamedTemporaryFile('w') as f:
            tracefile = Tracefile(f.name)
            tracefile.arch = 'aarch64'
            tracefile.add(capabilities={'kill'}, syscalls={'sync'})
        self.assertEqual(str(tracefile), dedent('''\
            ARCH
            aarch64

            CAPABILITIES
            kill

            SYSCALLS
            sync'''))

    def test_write(self):
        with tempfile.NamedTemporaryFile('w') as f:
            with Tracefile(f.name) as tracefile:
                pass
            with open(f.name, 'r') as f:
                self.assertIn('ARCH', f.read())

    def test_equal(self):
        tracefile1 = Tracefile('/abc')
        tracefile2 = Tracefile('/xyz')
        self.assertEqual(tracefile1, tracefile2)

    def test_not_equal(self):
        tracefile1 = Tracefile('/abc')
        tracefile2 = Tracefile('/xyz')
        tracefile2.add(syscalls='bpf')
        self.assertNotEqual(tracefile1, tracefile2)
