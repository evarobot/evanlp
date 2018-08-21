#!/usr/bin/env python
# encoding: utf-8

import json
import unittest
import tornado
from tornado.testing import AsyncHTTPTestCase

from vikinlp.controller import init_controllers
from vikinlp import config, data
from vikinlp.libs.route import Route
from vikinlp.util import uniout

config.init()
data.init()
init_controllers()
urls = Route.routes()
tornado_app = tornado.web.Application(urls)


class TestRecommender(AsyncHTTPTestCase):
    """ 测试推荐系统"""

    def get_app(self):
        return tornado_app

    def test_temp(self):

        data = {
            'sex': 'male',
            'age': 56,
            'with_kid': True
        }

        params = {
            'robotid': '12345',
            'appname': 'Maccaw',
            'data': data,
            'version': 0.1
        }

        res = self.fetch("/viki/recommend",
                         body=json.dumps(params),
                         method="POST")
        if not str(res.code).startswith("20"):
            errmsg = "服务器异常：http code-%s" % res.code
            raise Exception(uniout.unescape(errmsg, None))


if __name__ == '__main__':
    unittest.main()
