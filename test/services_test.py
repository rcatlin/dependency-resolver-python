""" Services Module Unit Tests"""
import unittest

from example_classes import Bar
from example_classes import Foo
from example_classes import Spam
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
