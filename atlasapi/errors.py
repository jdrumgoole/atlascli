
class AtlasError(ValueError):
    pass


class AtlasAuthenticationError(AtlasError):
    pass


class AtlasGetError(AtlasError):
    pass


class AtlasPostError(AtlasError):
    pass


class AtlasPatchError(AtlasError):
    pass


class AtlasEnvironmentError(ValueError):
    pass


class AtlasInitialisationError(ValueError):
    pass
