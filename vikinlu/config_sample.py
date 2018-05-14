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


class _ConfigRedis:
    _host = "viki_redis"
    _port = 6379
    _db = 1

    @property
    def host(self):
        hst = os.environ.get("REDIS_HOST")
        return hst if hst is not None else self._host

    @property
    def port(self):
        prt = os.environ.get("REDIS_PORT")
        return prt if prt is not None else self._port

    @property
    def db(self):
        d = os.environ.get("REDIS_DB")
        return d if d is not None else self._db


class _ConfigMongoTest:
    _host = "127.0.0.1"
    _port = 27017
    _db = "eve_test"

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


class _ConfigApps(object):
    _cache_data_path = "/src/data/caches"
    _model_data_path = "/src/data/models"

    @property
    def cache_data_path(self):
        hst = os.environ.get("CACHE_DATA_PATH")
        return hst if hst is not None else self._cache_data_path

    @property
    def model_data_path(self):
        hst = os.environ.get("MODEL_DATA_PATH")
        return hst if hst is not None else self._model_data_path


class _ConfigNeo4j:
    _host = "127.0.0.1"
    _port = 7474
    _namespace = "Cosmetics"

    @property
    def host(self):
        hst = os.environ.get("NEO4J_HOST")
        return hst if hst is not None else self._host

    @property
    def port(self):
        prt = os.environ.get("NEO4j_PORT")
        return int(prt) if prt is not None else self._port

    @property
    def namespace(self):
        d = os.environ.get("NEO4j_NAMESPACE")
        return d if d is not None else self._namespace


class _ConfigDeploy(object):
    """"""
    deploy = "dev"
    #deploy = "production"


ConfigMongoTest = _ConfigMongoTest()
ConfigMongo = _ConfigMongo()
ConfigRedis = _ConfigRedis()
ConfigLog = _ConfigLog()
ConfigApps = _ConfigApps()
ConfigNeo4j = _ConfigNeo4j()
ConfigDeploy = _ConfigDeploy()
