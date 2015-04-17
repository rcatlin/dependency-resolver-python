""" Services Module Unit Tests"""
import unittest

from example_classes import Bar
from example_classes import Foo
from example_classes import Spam
from example_classes import Weeble
from services import ServiceFactory


class ServiceFactoryTest(unittest.TestCase):
    """ Service Factory Unit Tests """
    def setUp(self):
        self._factory = ServiceFactory({
            'flib': 'FLIB',
            'flub': 'FLUB',
            'new_ham': 'new ham',
            'new_eggs': 'new eggs'
        })

    def test_replace_services(self):
        foo = Foo()
        self._factory.add_instantiated_service('foo', foo)

        self.assertEquals(
            [foo],
            self._factory._replace_services_in_args(['@foo'])
        )
        self.assertEquals(
            [[foo]],
            self._factory._replace_services_in_args([['@foo']])
        )
        self.assertEquals(
            ['bar', {'foo': foo}],
            self._factory._replace_services_in_args(['bar', {'foo': '@foo'}])
        )
        self.assertEquals(
            [('bar', 'baz'), {'foo': foo}],
            self._factory._replace_services_in_args([('bar', 'baz'), {'foo':'@foo'}])
        )
        self.assertEquals(
            {'foo': foo},
            self._factory._replace_services_in_kwargs({'foo': '@foo'})
        )
        self.assertEquals(
            {'config': {'foo': foo}},
            self._factory._replace_services_in_kwargs({'config': {'foo': '@foo'}})
        )
        self.assertEquals(
            {'bar': {'baz': [foo]}},
            self._factory._replace_services_in_kwargs({'bar': {'baz': ['@foo']}})
        )
        # No replacement
        self.assertEquals(
            [{'foo': 1000}],
            self._factory._replace_services_in_args([{'foo': 1000}])
        )
        self.assertEquals(
            {'foo': 1000},
            self._factory._replace_services_in_kwargs({'foo': 1000})
        )

    def test_replace_scalars(self):
        self.assertEquals(
            ['FLIB'],
            self._factory._replace_scalars_in_args(['$flib'])
        )
        self.assertEquals(
            [['FLIB']],
            self._factory._replace_scalars_in_args([['$flib']])
        )
        self.assertEquals(
            ['bar', {'foo': 'FLIB'}],
            self._factory._replace_scalars_in_args(['bar', {'foo': '$flib'}])
        )
        self.assertEquals(
            [('bar', 'baz'), {'foo': 'FLIB'}],
            self._factory._replace_scalars_in_args([('bar', 'baz'), {'foo':'$flib'}])
        )
        self.assertEquals(
            {'foo': 'FLIB'},
            self._factory._replace_scalars_in_kwargs({'foo': '$flib'})
        )
        self.assertEquals(
            {'flib': 'FLIB', 'flub': 'FLUB'},
            self._factory._replace_scalars_in_kwargs({
                'flib': '$flib',
                'flub': '$flub'
            })
        )
        self.assertEquals(
            {'config': {'foo': 'FLIB'}},
            self._factory._replace_scalars_in_kwargs({'config': {'foo': '$flib'}})
        )
        self.assertEquals(
            {'bar': {'baz': ['FLIB']}},
            self._factory._replace_scalars_in_kwargs({'bar': {'baz': ['$flib']}})
        )

    def test_create(self):
        """ Simple Factory call with scalars """
        result = self._factory.create('example_classes', 'Foo')
        assert isinstance(result, Foo)

        #  Test with scalar params
        result = self._factory.create(
            'example_classes',
            'Spam',
            kwargs={
                'ham': '$flib',
                'eggs': '$flub'
            }
        )
        assert isinstance(result, Spam)
        self.assertEquals(result.ham, 'FLIB')
        self.assertEquals(result.eggs, 'FLUB')

    # pylint: disable=invalid-name
    def test_factory_with_no_args_or_kwargs(self):
        """ Factory call with no args/kwargs """
        result = self._factory.create(
            'example_classes',
            'Factory',
            [],
            {},
            'get_foo'
        )
        assert isinstance(result, Foo)

    def test_factory_with_args(self):
        """ Factory call with args """
        result = self._factory.create(
            'example_classes',
            'Factory',
            [],
            {},
            'get_spam',
            ['HAM!', 'eggz'],
            {}
        )
        assert isinstance(result, Spam)
        self.assertEquals(result.ham, 'HAM!')
        self.assertEquals(result.eggs, 'eggz')

    def test_factory_with_kwargs(self):
        """ Factory call with kwargs """
        result = self._factory.create(
            'example_classes',
            'Factory',
            [],
            {},
            'get_more_spam',
            [],
            {'ham': 'ahm', 'eggs': 'segg'}
        )
        assert isinstance(result, Spam)
        self.assertEquals(result.ham, 'ahm')
        self.assertEquals(result.eggs, 'segg')

    def test_factory_with_calls(self):
        """ Factory call with extra calls """
        result = self._factory.create(
            'example_classes',
            'Factory',
            [],
            {},
            'get_spam',
            ['just ham', 'just eggs'],
            {},
            False,
            [
                {
                    'method': 'set_ham',
                    'args': ['$new_ham'],
                    'kwargs': {}
                },
                {
                    'method': 'set_eggs',
                    'args': [],
                    'kwargs': {'eggs': '$new_eggs'}
                }
            ]
        )
        assert isinstance(result, Spam)
        self.assertEquals(result.ham, 'new ham')
        self.assertEquals(result.eggs, 'new eggs')

    def test_static(self):
        """ Static Factory call """
        result = self._factory.create(
            'example_classes',
            'Wibble',
            [],
            {},
            None,
            [],
            {},
            True
        )
        self.assertEquals(result.value, 'wobble')

    def test_create_with_service(self):
        """ Instantiate a Service with an existing Service defined """
        # pylint: disable=blacklisted-name
        foo = Foo()
        self._factory.add_instantiated_service('foo', foo)
        result = self._factory.get_instantiated_service('foo')
        assert isinstance(result, Foo)

        result = self._factory.create(
            'example_classes',
            'Bar',
            ['@foo']
        )

        assert isinstance(result, Bar)

    def test_create_with_nested_scalars(self):
        """ Instantate a Service with nested scalar """
        config = {
            'foo': {
                'bar': {'flib': '$flib'},
                'baz': ['$flub']
            }
        }
        result = self._factory.create(
            'example_classes',
            'Weeble',
            [config]
        )

        assert isinstance(result, Weeble)
        self.assertEquals(
            result.find('foo'),
            {
                'bar': {'flib': 'FLIB'},
                'baz': ['FLUB']
            }
        )
