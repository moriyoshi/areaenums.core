# encoding: utf-8

import re

from zope.interface import implementer
from zope.interface.verify import verifyObject

from zope.i18n.locales import locales, LocaleIdentity
from zope.i18n.interfaces.locales import ILocale, ILocaleIdentity

from .interfaces import IGeoDivision, IGeoDivisionProvider, IMutableGeoDivisionRegistry
from .exceptions import RegistryAlreadyExists, RegistryNotFound, DivisionNotFound, BadLocaleString

__all__ = [
    'DivisionBase',
    'SimpleDivision',
    'DefaultGeoDivisionProvider',
    'lookupDivisionRecursively',
    'lookupLocaleTree',
    'parseLocaleIdentity',
    'localeIdentityToString',
    'toLocale',
    'earth',
    'provider',
    ]

class DivisionBase(object):
    @property
    def belongs_to(self):
        return self._belongs_to

    def getRegistries(self):
        return self._registries.values()

    def _populateDivisionMap(self):
        if not self._id_to_division_map:
            id_to_division_map = {}
            name_to_division_map = {}
            for registry in self._registries.values():
                if not IGeoDivision.providedBy(registry):
                    continue
                id_to_division_map[registry.id] = registry
                name_to_division_map[registry.name] = registry
                for _, localizedName in registry.getLocalizedNames():
                    name_to_division_map[localizedName] = registry
            self._id_to_division_map = id_to_division_map
            self._name_to_division_map = name_to_division_map

    def getDivisions(self):
        self._populateDivisionMap()
        return self._id_to_division_map.values()

    def getDivisionById(self, id):
        self._populateDivisionMap()
        try:
            return self._id_to_division_map[id]
        except KeyError:
            raise DivisionNotFound(id)

    def getDivisionByName(self, name):
        self._populateDivisionMap()
        try:
            return self._name_to_division_map[name]
        except KeyError:
            raise DivisionNotFound(name)

    def getDivisionByLocalId(self, id):
        return self.getDivisionById(id)

    def queryRegistry(self, name):
        try:
            return self._registries[name]
        except KeyError:
            raise RegistryNotFound(name)

    def addRegistry(self, registry):
        if registry.name in self._registries:
            raise RegistryAlreadyExists(registry.name)
        registry._bind(self)
        self._registries[registry.name] = registry

    def _bind(self, registry):
        self._belongs_to = registry

    def __init__(self):
        self._id_to_division_map = None
        self._name_to_division_map = None
        self._belongs_to = None
        self._registries = {}


@implementer(IGeoDivision, IMutableGeoDivisionRegistry)
class SimpleDivision(DivisionBase):
    def getLocalizedNames(self):
        return [(parseLocaleIdentity(iso), value) for iso, value in self._raw_localized_names.items()]

    def getLocalizedName(self, iso):
        for _locale in lookupLocaleTree(toLocale(iso)):
            value = self._raw_localized_names.get(localeIdentityToString(_locale.id))
            if value is not None:
                return value
        return self.name

    def __init__(self, id, name, level, longitude=None, latitude=None, local_id=None, localized_names={}):
        super(SimpleDivision, self).__init__()
        self.id = id
        self.name = name
        self.level = level
        self.longitude = longitude
        self.latitude = latitude
        self.localId = local_id
        self._raw_localized_names = localized_names
        self._localized_names = None

@implementer(IGeoDivisionProvider)
class DefaultGeoDivisionProvider(object):
    def getRootDivision(self):
        return self.root

    def getDivisionById(self, id):
        return lookupDivisionRecursively(self.root, id)

    def __init__(self, root):
        self.root = root

def lookupDivisionRecursively(registry, id):
    try:
        return registry.getDivisionById(id)
    except DivisionNotFound:
        pass
    
    for subregistry in registry.getRegistries():
        try:
            return subregistry.getDivisionById(id)
        except DivisionNotFound:
            pass
        try:
            return lookupDivisionRecursively(subregistry, id)
        except DivisionNotFound:
            pass
    raise DivisionNotFound(id)

def lookupLocaleTree(locale):
    while True:
        yield locale
        try:
            locale = locale.getInheritedSelf()
        except:
            break

LOCALE_STR_REGEX = re.compile('([A-Za-z]{2,3})(?:_([A-Za-z]{2,3})(?:@([_A-Za-z][_0-9A-Za-z]*))?)?')
def parseLocaleIdentity(iso):
    g = re.match(LOCALE_STR_REGEX, iso)
    if not g:
        raise BadLocaleString(iso)

    language = g.group(1).lower()
    territory = g.group(2)
    if territory is not None:
        territory = territory.lower() 
    variant = g.group(3)
    if variant is not None:
        variant = variant.lower()
    return LocaleIdentity(
        language=language,
        territory=territory,
        variant=variant
        )

def localeIdentityToString(localeIdentity):
    retval = []
    if localeIdentity.language:
        retval.append(localeIdentity.language.lower())
    if localeIdentity.territory:
        retval.append('_')
        retval.append(localeIdentity.territory.upper())
    if localeIdentity.variant:
        retval.append('@')
        retval.append(localeIdentity.variant)
    return ''.join(retval)

def toLocale(iso):
    locale = None
    if ILocale.providedBy(iso):
        locale = iso
    else:
        localeIdentity = None
        if isinstance(iso, basestring):
            localeIdentity = parseLocaleIdentity(iso)
        elif ILocaleIdentity.providedBy(iso):
            localeIdentity = iso 
        if localeIdentity is not None:
            locale = locales.getLocale(localeIdentity.language, localeIdentity.territory, localeIdentity.variant)
    if locale is None:
        raise TypeError('the argument must be a string, ILocaleIdentity or ILocale')
    return locale

earth = SimpleDivision(
    id=0,
    name=u'The Earth',
    level=0,
    longitude=None,
    latitude=None,
    localized_names={
        u'en': u'The Earth',
        u'ja': u'地球',
        }
    )

provider = DefaultGeoDivisionProvider(earth)
