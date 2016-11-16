"""
Interact with CCC services
"""
from ccc_client.DtsRunner import DtsRunner
from ccc_client.DcsRunner import DcsRunner
from ccc_client.AppRepoRunner import AppRepoRunner
from ccc_client.ExecEngineRunner import ExecEngineRunner
from ccc_client.ElasticSearchRunner import ElasticSearchRunner
from ccc_client.EveMongoRunner import EveMongoRunner

__all__ = ["DtsRunner",
           "DcsRunner",
           "AppRepoRunner",
           "ExecEngineRunner",
           "ElasticSearchRunner",
           "EveMongoRunner"]

__version__ = "undefined"
try:
    import ccc_client._version
    __version__ = ccc_client._version.version
except ImportError:
    pass
