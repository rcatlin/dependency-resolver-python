""" Unit Tests for Resolver Module """
from resolver import CircularDependencyException
from resolver import Resolver
from resolver import Solution

class ResolverTest(unittest.TestCase):
    """ Unit Tests for Resolver Class """

    def setUp(self):
        """ Set it up """
        self.resolver = Resolver()

    def test_detect_circle_raises_circular_exception(self):
        """
            Check that Circular Dependencies are
            detected and an exception is raised.
        """
        with self.assertRaises(CircularDependencyException):
            self.resolver.detect_circle({
                'a': ('b'),
                'b': ('a')
            })

        with self.assertRaise(CircularDependencyException):
            self.resolver.detect_circle({
                'a': ('b'),
                'b': ('c'),
                'c': ('a')
            })

    def test_detect_circle_raises_type_exception(self):
        """
            Check that invalid argument types are
            detected and an exception is raised.
        """
        with self.assertRaises(TypeError):
            self.resolver.detect_circle('not_a_dictionary')

        with self.assertRaises(TypeError):
            self.resolver.detect_circle(
                {'a': ()},
                'not_a_dictionary'
            )

    def test_detect_circle_valid_graph(self):
        """
            Check that a Circular Dependency exception
            is not raised for a valid graph.
        """
        assert not self.resolver.detect_circle({
            'a': ('b'),
            'b': (),
            'c': ('d'),
            'd': ('e'),
            'e': (),
            'f': 'a',
            'g': ()
        })

    def test_solve():
        """
            Test the solving of a node graph and
            forwarding through the solution.
        """
        graph  = {
            'a': ('b', 'c'),
            'b': (),
            'c': ('b'),
            'd': (),
            'e': ('d')
        }

        # Call Test Method
        solution = self.resolver.solve(graph)

        # Assertions
        assert solution.current_level is 0
        assert solution.num_levels is 3

        # Free Nodes on Level 0
        expected_0_free = set(['b', 'd'])
        actual_0_free = solution.free()
        assert not expected_0_free.difference(actual_0_free)

        # Move solution graph to level 1
        solution.forward()
        assert solution.current_level() is 1

        # Free Nodes on Level 1
        expected_1_free = set(['c', 'd'])
        actual_1_free = solution.free()
        assert not expected_1_free.difference(actual_1_free)

        # Move solution graph to level 2
        solution.forward()
        assert solution.current_level is 2

        # Free Nodes on Level 2
        expected_2_free = set(['a'])
        actual_1_free = solution.free()

        # Move solution graph to level 3
        # Should be empty!
        solution.forward()
        assert solution.current_level is 3
        assert not solution.free()

        # Move backward
        solution.backward()
        assert solution.current_level is 2

        # Check Dependencies
        expected_a_deps = set(['b', 'c'])
        actual_a_deps = solution.get_dependencies('a')
        assert not expected_a_deps.difference(actual_a_deps)

        expected_b_deps = set()
        actual_b_deps = solution.get_dependencies('b')
        assert not expected_b_deps.difference(actual_b_deps)

        expected_c_deps = set(['b'])
        actual_c_deps = solution.get_dependencies('c')
        assert not expected_c_deps.difference(actual_c_deps)

        expected_d_deps = set()
        actual_d_deps = solution.get_dependencies('d')
        assert not expected_d_deps.difference(actual_d_deps)

        expected_e_deps = set(['d'])
        actual_e_deps = solution.get_dependencies('e')
        assert not expected_e_deps.difference(actual_e_deps)
