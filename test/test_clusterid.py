import unittest

from atlascli.clusterid import ClusterID, ProjectID


class TestClusterID(unittest.TestCase):

    def test_project_id(self):
        p = ProjectID("5f9402a18a7db74dcaef39c8")
        self.assertEqual(p.id, "5f9402a18a7db74dcaef39c8")
        with self.assertRaises(ValueError):
            p = ProjectID("5f9402a18a7db74dcaefXXXX")
        with self.assertRaises(ValueError):
            p = ProjectID("5f9402a18a7db74dcaef")

        p = ProjectID("5f9402a18a7db74dcaef", throw_exception=False)
        self.assertEqual(p.id, None)

    def test_cluster_id(self):
        c = ClusterID("5f9402a18a7db74dcaef39c8", "stackoverflow")
        self.assertEqual(c.project_id, "5f9402a18a7db74dcaef39c8")
        self.assertEqual(c.name, "stackoverflow")

        with self.assertRaises(ValueError):
            _ = ClusterID(None, "tester")

        with self.assertRaises(ValueError):
            _ = ClusterID("", "tester")

    def test_constraints(self):
        with self.assertRaises(ValueError):
            c = ClusterID("5f9402a18a7db74dcaef39c8____", "stackoverflow")

        with self.assertRaises(ValueError):
            c = ClusterID("5f9402a18a7db74dcaef39c8", "stackoverflow_")

        c = ClusterID("5f9402a18a7db74dcaef39c8", "stackoverflow_", throw_exception=False)
        self.assertEqual(c.project_id, "5f9402a18a7db74dcaef39c8")
        self.assertEqual(c.name, None)

        with self.assertRaises(ValueError):
            c = ClusterID("5f9402", "stackoverflow_")

    def test_parse(self):
        c = ClusterID.parse("5f9402a18a7db74dcaef39c8:stackoverflow")
        self.assertEqual(c.project_id,"5f9402a18a7db74dcaef39c8")
        self.assertEqual(c.name, "stackoverflow")

    def test_eq(self):
        a = ClusterID.parse("5f9402a18a7db74dcaef39c8:stackoverflow")
        b = ClusterID.parse("5f9402a18a7db74dcaef39c8:stackoverflow")
        c = ClusterID.parse("5f9402a18a7db74dcaef39c8:differentname")
        d = ClusterID.parse("5f9402a18a7db74d999939c8:differentname")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)

if __name__ == '__main__':
    unittest.main()
