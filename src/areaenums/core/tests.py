# encoding: utf-8

from unittest import TestCase
from mock import Mock
from zope.interface import implementer
from zope.i18n.locales import locales, LocaleIdentity
from .division import SimpleDivision, DefaultGeoDivisionProvider, earth, provider, parseLocaleIdentity
from .exceptions import DivisionNotFound, RegistryNotFound
from .interfaces import IGeoDivision, IGeoDivisionRegistry

class TestDefaultGeoDivisionProvider(TestCase):
    def test_getRootDivision(self):
        mockGeoDivision = Mock()
        provider = DefaultGeoDivisionProvider(mockGeoDivision)
        self.assertEquals(provider.getRootDivision(), mockGeoDivision)

    def test_getDivisionById(self):
        class MockGeoDivision(object):
            def __init__(self):
                self.registries = [Mock(**{
                    'getDivisionById.return_value': 2
                    })]

            def getDivisionById(self, id):
                if id == 0:
                    return 0
                else:
                    raise DivisionNotFound()

            def getRegistries(self):
                return self.registries

        mock = MockGeoDivision()
        provider = DefaultGeoDivisionProvider(mock)
        self.assertEquals(provider.getDivisionById(0), 0)
        self.assertEquals(provider.getDivisionById(1), 2)
        mock.registries[0].getDivisionById.assert_called_with(1)


class TestEarth(TestCase):
    def test_name(self):
        self.assertEquals(earth.name, u'The Earth')

    def test_getLocalizedName(self):
        self.assertEquals(earth.getLocalizedName(LocaleIdentity()), u'The Earth')
        self.assertEquals(earth.getLocalizedName(locales.getLocale('en').id), u'The Earth')
        self.assertEquals(earth.getLocalizedName(locales.getLocale('ja').id), u'地球')


class TestSimpleDivision(TestCase):
    def _makeDivision(self):
        return SimpleDivision(u'root', u'root', 0)

    def test_addRegistry(self):
        @implementer(IGeoDivisionRegistry)
        class DummyRegistry(object):
            name = u'registry'

            def _bind(self, registry):
                self.belongs_to = registry

            def getRegistries(self):
                return []

            def getDivisionById(id):
                raise DivisionNotFound()

            def queryRegistry(name):
                raise RegistryNotFound()
             
        @implementer(IGeoDivision)
        class DummyDivision(object):
            id = 1
            name = u'division'
            level = 1
            localId = 1
            longitude = None
            latitude = None

            def _bind(self, registry):
                self.belongs_to = registry

            def getRegistries(self):
                return []

            def getDivisionById(self, id):
                raise DivisionNotFound()

            def queryRegistry(self, name):
                raise RegistryNotFound()

            def getLocalizedNames(self):
                return [(locales.getLocale('en').id, u'テスト')]

            def getLocalizedName(self, localeIdentity):
                for localeIdentity, localizedName in self.getLocalizedNames():
                    if localeIdentity == localeIdentity:
                        return localizedName
                raise DivisionNotFound()

            def getDivisions():
                return []

            def getDivisionByLocalId(id):
                raise DivisionNotFound()

            def getDivisionByName(name):
                raise DivisionNotFound()

             
        target = self._makeDivision()
        dummyRegistry = DummyRegistry()
        dummyDivision = DummyDivision()
        target.addRegistry(dummyRegistry)
        self.assertEqual(dummyRegistry.belongs_to, target)
        target.addRegistry(dummyDivision)
        self.assertEqual(dummyDivision.belongs_to, target)

        self.assertRaises(DivisionNotFound, lambda: target.getDivisionByName(u'registry'))
        self.assertEqual(target.getDivisionByName(u'division'), dummyDivision)
        self.assertRaises(DivisionNotFound, lambda: target.getDivisionById(0))
        self.assertEqual(target.getDivisionById(1), dummyDivision)

class TestParseLocaleIdentity(TestCase):
    def test(self):
        identity = parseLocaleIdentity('en')
        self.assertEqual(identity.language, 'en')
        self.assertEqual(identity.territory, None)
        self.assertEqual(identity.variant, None)

        identity = parseLocaleIdentity('EN')
        self.assertEqual(identity.language, 'en')
        self.assertEqual(identity.territory, None)
        self.assertEqual(identity.variant, None)

        identity = parseLocaleIdentity('en_US')
        self.assertEqual(identity.language, 'en')
        self.assertEqual(identity.territory, 'us')
        self.assertEqual(identity.variant, None)

        identity = parseLocaleIdentity('en_us')
        self.assertEqual(identity.language, 'en')
        self.assertEqual(identity.territory, 'us')
        self.assertEqual(identity.variant, None)

        identity = parseLocaleIdentity('en_US@variant')
        self.assertEqual(identity.language, 'en')
        self.assertEqual(identity.territory, 'us')
        self.assertEqual(identity.variant, 'variant')

        identity = parseLocaleIdentity('en_US@Variant')
        self.assertEqual(identity.language, 'en')
        self.assertEqual(identity.territory, 'us')
        self.assertEqual(identity.variant, 'variant')

