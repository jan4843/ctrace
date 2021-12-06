import unittest
from ctrace.lookup import capabilities


class TestCapabilities(unittest.TestCase):
    def test_ids_nonempty(self):
        ids = capabilities.ids.keys()
        self.assertGreater(len(ids), 0)

    def test_names_nonempty(self):
        names = capabilities.names.keys()
        self.assertGreater(len(names), 0)

    def test_get_id(self):
        id_ = capabilities.ids['chown']
        self.assertEqual(id_, 0)

    def test_get_id_unformatted(self):
        id_ = capabilities.ids['CAP_CHOWN']
        self.assertEqual(id_, 0)

    def test_get_name(self):
        name = capabilities.names[0]
        self.assertEqual(name, 'chown')

    def test_get_inexistent_id(self):
        with self.assertRaises(KeyError):
            capabilities.ids['non_existing_cap']

    def test_get_inexistent_name(self):
        with self.assertRaises(KeyError):
            capabilities.names[9999999]
