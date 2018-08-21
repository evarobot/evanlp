# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import tornado.httpserver
from tornado.options import define, parse_command_line, options

from vikinlp.util.log import add_tornado_log_handler
from vikinlp.config import ConfigLog
from vikinlp.libs.route import Route
from vikinlp.controller import init_controllers
from vikinlp import config, data


define("port", type=int, default=7000,
       help="the server port")
define("address", type=str, default='0.0.0.0',
       help="the server address")
define("debug", type=bool, default=False,
       help="switch debug mode")
parse_command_line()

config.init()
data.init()
init_controllers()

urls = Route.routes()
add_tornado_log_handler(ConfigLog.log_path, ConfigLog.log_level)

application = tornado.web.Application(urls, cookie_secret="fa5012f23340edae6db5df925b345912", autoreload=True)
app_server = tornado.httpserver.HTTPServer(application, xheaders=True)
app_server.listen(options.port, options.address)
tornado.ioloop.IOLoop.instance().start()
