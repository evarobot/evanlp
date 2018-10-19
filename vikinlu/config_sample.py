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


class _ConfigMongo(object):
    _host = "39.108.48.176"
    _port = 27017
    _password = "testmg@ns"
    _db = "eve"
    _user = 'root'

    def __init__(self):
        self.db = os.environ.get("MONGO_DB", self._db)
        self.host = os.environ.get("MONGO_HOST", self._host)
        self.port = os.environ.get("MONGO_PORT", self._port)
        self.username = os.environ.get("MONGO_USER", self._user)
        self.password = os.environ.get("MONGO_PORT", self._password)
        self.authentication_source = 'admin'

    @property
    def MONGODB_SETTINGS(self):
        return self.__dict__


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


class _Config:

    _host = "0.0.0.0"
    _port = 8888
    _debug = "False"

    @staticmethod
    def init_app(app):
        app.config["IMAGE_UPLOAD_PATH"] = os.path.join(
            app.config["MEDIA_PATH"], "image")
        app.config["APK_UPLOAD_PATH"] = os.path.join(app.config["MEDIA_PATH"],
                                                     "apk")
        app.config["VIDEO_UPLOAD_PATH"] = os.path.join(
            app.config["MEDIA_PATH"], "video")

    @property
    def host(self):
        host = os.environ.get("NLU_HOST")
        return host if host is not None else self._host

    @property
    def port(self):
        port = os.environ.get("NLU_PORT")
        return port if port is not None else self._port

    @property
    def debug(self):
        debug = os.environ.get("DEBUG")
        return debug if debug is not None else self._debug


ConfigMongo = _ConfigMongo()
ConfigLog = _ConfigLog()
ConfigData = _ConfigData()
Config = _Config()
