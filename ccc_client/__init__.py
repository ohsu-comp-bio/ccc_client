"""
Interact with CCC services
"""
from ccc_client.dts.DtsRunner import DtsRunner
from ccc_client.dcs.DcsRunner import DcsRunner
from ccc_client.app_repo.AppRepoRunner import AppRepoRunner
from ccc_client.exec_engine.ExecEngineRunner import ExecEngineRunner

__all__ = ["DtsRunner",
           "DcsRunner",
           "AppRepoRunner",
           "ExecEngineRunner"]

__version__ = "undefined"
try:
    import ccc_client._version
    __version__ = ccc_client._version.version
except ImportError:
    pass
