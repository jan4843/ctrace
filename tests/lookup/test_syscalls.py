import unittest
from ctrace.lookup import syscalls


class TestSyscalls(unittest.TestCase):
    def test_ids_nonempty(self):
        ids = syscalls.ids.keys()
        self.assertGreater(len(ids), 0)

    def test_names_nonempty(self):
        names = syscalls.names.keys()
        self.assertGreater(len(names), 0)

    def test_get_id(self):
        id_ = syscalls.ids['clone3']
        self.assertEqual(id_, 435)

    def test_get_id_unformatted(self):
        id_ = syscalls.ids['CLONE3']
        self.assertEqual(id_, 435)

    def test_get_name(self):
        name = syscalls.names[435]
        self.assertEqual(name, 'clone3')

    def test_get_inexistent_id(self):
        with self.assertRaises(KeyError):
            syscalls.ids['non_existing_syscall']

    def test_get_inexistent_name(self):
        with self.assertRaises(KeyError):
            syscalls.names[9999999]
