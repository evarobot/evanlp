# encoding=utf-8
"""
推荐系统API
"""
import json
import time
from vikinlp.libs.handler import RobotAPIHandler
from vikinlp.libs.route import Route
from vikinlp.rec import recommendor
from vikinlp.util.log import gen_log as log


@Route('/viki/recommend/?')
class QAHandler(RobotAPIHandler):

    def post(self):
        return self.get()

    def get(self):
        data = self.data
        log.info("[RECReceive %s_%s]: %s" % (data['appname'], data['robotid'], data))
        try:
            data['data']['time'] = time.strftime("%H:%M:%S", time.localtime())
            rec = recommendor[data['appname'].lower()]
        except KeyError as e:
            log.exception(e)
            ret = {'error': 'None exist app: %s' % data['appname']}
        else:
            key, tts = rec.recommend(data['data'])
            ret = {
                'key': key.encode('utf8'),
                'tts': tts,
            }
        log.info("[RECResponse %s_%s]: %s" % (data['appname'], data['robotid'],
                                              json.dumps(ret, ensure_ascii=False)))
        return self.write_json(ret)
