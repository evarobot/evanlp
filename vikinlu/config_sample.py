# encoding=utf-8

'''
配置以Docker运行时为准，开发环境自己cp config.py后修改
'''

import os


class _ConfigLog(object):
    _log_level = 'INFO'
    _log_path = './'

    @property
    def log_level(self):
        lv = os.environ.get("LOG_LEVEL")
        return lv if lv is not None else self._log_level

    @property
    def log_path(self):
        lv = os.environ.get("LOG_LEVEL")
        return lv if lv is not None else self._log_path


class _ConfigMongo:
    _host = "127.0.0.1"
    _port = 27017
    _db = "eve"

    @property
    def host(self):
        hst = os.environ.get("MONGO_HOST")
        return hst if hst is not None else self._host

    @property
    def port(self):
        prt = os.environ.get("MONGO_PORT")
        return int(prt) if prt is not None else self._port

    @property
    def database(self):
        d = os.environ.get("MONGO_DB")
        return d if d is not None else self._db


class _ConfigData(object):
    _cache_data_path = "/src/data/caches"
    _model_data_path = "/src/data/models"
    _data_server_host = "127.0.0.1"
    _data_server_port = 8887

    @property
    def cache_data_path(self):
        hst = os.environ.get("CACHE_DATA_PATH")
        return hst if hst is not None else self._cache_data_path

    @property
    def model_data_path(self):
        hst = os.environ.get("MODEL_DATA_PATH")
        return hst if hst is not None else self._model_data_path

    @property
    def data_server_host(self):
        hst = os.environ.get("DATA_SERVER_HOST")
        return hst if hst is not None else self._data_server_host

    @property
    def data_server_port(self):
        hst = os.environ.get("DATA_SERVER_PORT")
        return hst if hst is not None else self._data_server_port



ConfigMongo = _ConfigMongo()
ConfigLog = _ConfigLog()
ConfigData = _ConfigData()
