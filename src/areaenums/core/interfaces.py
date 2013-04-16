from zope.interface import Interface, Attribute

class IGeoDivisionRegistry(Interface):
    name = Attribute('''name''')

    def _bind(target):
        """Internally used when associating a division to its subdivision"""

    def getRegistries():
        """Returns the sub-registries"""

    def getDivisionById(id):
        """Returns the subdivision by geoname id"""

    def queryRegistry(name):
        """Queries the registry by name"""

class IMutableGeoDivisionRegistry(IGeoDivisionRegistry):
    def addRegistry(registry):
        """Associate a sub-registry to this registry"""

class IGeoDivision(IGeoDivisionRegistry):
    id = Attribute('''a geoname id''')
    level = Attribute('''level''')
    localId = Attribute('''an identifier specific to this division''')
    longitude = Attribute('''longitude''')
    latitude = Attribute('''latitude''')
    belongs_to = Attribute('''belongs_to''')

    def getLocalizedNames():
        '''Returns alternative names'''

    def getLocalizedName(localeIdentity):
        """Returns the localized name"""

    def getDivisions():
        """Returns the subdivisions that belong to this division"""

    def getDivisionByLocalId(id):
        """Returns the subdivision by id that is unique (at least) amongst this division"""

    def getDivisionByName(name):
        """Returns the subdivision by name"""

class IGeoDivisionProvider(Interface):
    def getRootDivision():
        """Gets the root division"""

    def getDivisionById(id):
        """Returns the subdivision by geoname id"""
