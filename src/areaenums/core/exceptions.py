class AreaEnumsError(Exception):
    pass

class DivisionNotFound(AreaEnumsError):
    pass

class RegistryNotFound(AreaEnumsError):
    pass

class RegistryAlreadyExists(AreaEnumsError):
    pass

class BadLocaleString(AreaEnumsError):
    pass
