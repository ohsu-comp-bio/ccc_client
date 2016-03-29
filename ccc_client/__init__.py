"""
Interact with CCC services
"""
from ccc_client.DtsRunner import DtsRunner
from ccc_client.AppRepoRunner import AppRepoRunner
from ccc_client.ExecEngineRunner import ExecEngineRunner

__all__ = ["DtsRunner", "AppRepoRunner", "ExecEngineRunner"]

__version__ = "undefined"
try:
    import ccc_client._version
    __version__ = ccc_client._version.version
except ImportError:
    pass
