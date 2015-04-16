""" Unit Tests for Resolver Module """
import unittest
import yaml

from example_classes import Bar
from example_classes import Baz
from example_classes import Foo
from example_classes import Spam
from example_classes import Qux
from example_classes import Wobble
from resolver import CircularDependencyException
from resolver import detect_circle
from resolver import _detect_circle
from resolver import is_dependency_name
from resolver import Resolver
from tree import DependencyTree


def get_config_yaml():
    """ Load test config YAML file """
    return yaml.load(open('test/test_config.yaml', 'r')) or {}


class DetectCircleTest(unittest.TestCase):
    """ Unit Tests for detect_circle method """
    # pylint: disable=no-self-use, invalid-name
    def test_detect_circle_raises_circular_exception(self):
        """
            Check that Circular Dependencies are
            detected and an exception is raised.
        """
        with self.assertRaises(CircularDependencyException) as context:
            graph = {
                'a': set(['b']),
                'b': set(['a'])
            }
            detect_circle(graph)

        self.assertEquals(
            context.exception.node_path,
            'a->b->a'
        )

        with self.assertRaises(CircularDependencyException) as context:
            graph = {
                'a': set(['b']),
                'b': set(['c']),
                'c': set(['a'])
            }
            detect_circle(graph)

        self.assertEquals(
            context.exception.node_path,
            'a->b->c->a'
        )

    # pylint: disable=invalid-name
    def test_detect_circle_raises_type_exception(self):
        """
            Check that invalid argument types are
            detected and an exception is raised.
        """
        with self.assertRaises(TypeError):
            _detect_circle('not_a_dictionary')

        with self.assertRaises(TypeError):
            _detect_circle(
                {'a': ()},
                'not_a_tuple'
            )

        with self.assertRaises(TypeError):
            _detect_circle(
                {'a': ()},
                (),
                'not_a_list'
            )

        with self.assertRaises(TypeError):
            _detect_circle(
                {'a': ()},
                (),
                [],
                'not_an_integer'
            )

        with self.assertRaises(TypeError):
            _detect_circle(
                {'a': ()},
                (),
                [],
                0,
                'not_a_list'
            )

    # pylint: disable=no-self-use
    def test_detect_circle_2(self):
        """ Test another Circular Dependency Case """
        graph = {
            'a': set(['b']),
            'b': set(['c', 'd']),
            'c': set(['e']),
            'd': set(['e']),
            'e': set()
        }
        tree = detect_circle(graph)

        assert isinstance(tree, DependencyTree)

    def test_detect_circle(self):
        """
            Check that a Circular Dependency exception
            is not raised for a valid graph.
        """
        graph = {
            'a': set(['f', 'c']),
            'b': set(),
            'c': set(['b']),
            'd': set(),
            'e': set('d'),
            'f': set(),
            'g': set(['a'])
        }

        # Call Test Method
        tree = detect_circle(graph)
        assert isinstance(tree, DependencyTree)
        print tree
        self.assertEquals(7, tree.head_count)
        self.assertEquals(
            set(['d', 'a', 'c', 'b', 'e', 'g', 'f']),
            tree.head_values
        )


class DependencyNameTest(unittest.TestCase):
    """ Is dependency method Unit Tests """
    # pylint: disable=no-self-use
    def test_names(self):
        """ Assert correct service string values are detected """
        assert is_dependency_name('@foo')
        assert not is_dependency_name('foo')


class ResolverTest(unittest.TestCase):
    """ Resolver class Unit Tests """
    def test_init_nodes(self):
        """ Simple init nodes test """
        config = {
            'foo': {
                'module': 'example_classes',
                'class': 'Foo'
            }
        }
        resolver = Resolver(config)

        nodes = resolver.nodes
        self.assertEquals(nodes['foo'], set())

    # pylint: disable=invalid-name
    def test_init_nodes_with_a_dependency(self):
        """ Init nodes with a dependency """
        config = {
            'foo': {
                'module': 'example_classes',
                'class': 'Foo'
            },
            'bar': {
                'module': 'example_classes',
                'class': 'Bar',
                'args': ['@foo']
            }
        }
        resolver = Resolver(config)

        nodes = resolver.nodes
        self.assertEquals(nodes['foo'], set())
        self.assertEquals(nodes['bar'], set(['foo']))

    def test_init_nodes_complicated(self):
        """ Initialize nodes with advanced config YAML file """
        config = yaml.load(open('test/test_config.yml', 'r')) or {}
        resolver = Resolver(config)

        nodes = resolver.nodes
        self.assertEquals(nodes['baz'], set())
        self.assertEquals(nodes['foo'], set())
        self.assertEquals(nodes['bar'], set(['foo']))
        self.assertEquals(nodes['qux'], set(['foo', 'bar', 'baz']))

    def test_do_simple(self):
        """ Simple config resolution """
        resolver = Resolver({
            'foo': {
                'module': 'example_classes',
                'class': 'Foo'
            }
        })

        services = resolver.do()

        self.assertTrue('foo' in services)
        assert isinstance(services['foo'], Foo)

    def test_do_complicated(self):
        """ Instantiate services from advanced YAML file """
        config = yaml.load(open('test/test_config.yml', 'r')) or {}
        resolver = Resolver(config)

        services = resolver.do()

        assert isinstance(services['foo'], Foo)
        assert isinstance(services['bar'], Bar)
        assert isinstance(services['baz'], Baz)
        assert isinstance(services['qux'], Qux)
        assert isinstance(services['wobble'], Wobble)
        assert isinstance(services['spam'], Spam)

        spam = services['spam']
        self.assertEquals(spam.ham, 'ham!')
        self.assertEquals(spam.eggs, 'eggz')

        wobble = services['wobble']
        assert isinstance(wobble.foo, Foo)
        assert isinstance(wobble.bar, Bar)
        assert isinstance(wobble.baz, Baz)
        assert isinstance(wobble.spam, Spam)
