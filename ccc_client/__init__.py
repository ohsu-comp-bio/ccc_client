"""
Command line interface to CCC services
"""

__version__ = "undefined"
try:
    import _version
    __version__ = _version.version
except ImportError:
    pass
