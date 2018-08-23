# encoding: utf-8
import os


def init():
    pass


class _ConfigLog(object):
    _log_level = 'INFO'
    _log_path = '/var/log/vikidm'

    @property
    def log_level(self):
        lv = os.environ.get("LOG_LEVEL")
        return lv if lv is not None else self._log_level

    @property
    def log_path(self):
        lv = os.environ.get("LOG_LEVEL")
        return lv if lv is not None else self._log_path


class _ConfigApps(object):
    _cache_data_path = "/src/data/caches"
    _model_data_path = "/src/data/models"
    _nlp_data_path = os.path.realpath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "data"))

    @property
    def cache_data_path(self):
        hst = os.environ.get("CACHE_DATA_PATH")
        return hst if hst is not None else self._cache_data_path

    @property
    def model_data_path(self):
        hst = os.environ.get("MODEL_DATA_PATH")
        return hst if hst is not None else self._model_data_path

    @property
    def nlp_data_path(self):
        hst = os.environ.get("NLP_DATA_PATH")
        return hst if hst is not None else self._nlp_data_path


class _ConfigIO(object):
    _type = "FILE"

    @property
    def type(self):
        _type = os.environ.get("NLP_IO_TYPE")
        return _type if _type is not None else self._type


ConfigLog = _ConfigLog()
ConfigApps = _ConfigApps()
ConfigIO = _ConfigIO()
