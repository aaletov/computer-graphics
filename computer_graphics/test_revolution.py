import unittest

from .revolution import mesh_graph

class TestMeshGraph(unittest.TestCase):
    def test_plain(self):
        graph = mesh_graph((2, 2))

if __name__ == '__main__':
    unittest.main()