#!/usr/bin/env python
# encoding: utf-8

import logging
import mongoengine
import mock

from vikicommon.log import init_logger
from vikinlu.config import ConfigMongo
from vikinlu.filters import Sensitive
from vikinlu.robot import NLURobot
from vikinlu.util import cms_rpc
from vikinlu.intent import IntentRecognizer
from vikinlu import db
from evecms.models import (
    Domain,
    Slot
)

init_logger(level="DEBUG", path="./")
log = logging.getLogger(__name__)
dm_robot_id = "12345"

mongoengine.connect(db=ConfigMongo.database,
                    host=ConfigMongo.host,
                    port=ConfigMongo.port)
log.info('连接Mongo开发测试环境[eve数据库]成功!')


def test_sensitive():
    domain = Domain.objects.get(name="C")
    sensitive = Sensitive.get_sensitive(str(domain.pk))
    assert(set(sensitive._words) == set([u"共产党", u"毛泽东", u"法轮功"]))
    assert(sensitive.detect(u'共产党万岁') == True)
    assert(sensitive.detect(u'你叫什么') == False)



def test_integration_train():
    domain = Domain.objects.get(name="C")
    robot = NLURobot.get_robot(str(domain.pk))
    robot.train(("logistic", "0.1"))
    label_data = cms_rpc.get_tree_label_data(str(domain.pk))
    db.assert_intent_question(str(domain.pk), label_data)

db.clear_intent_question("C")


# TODO: casual talk test

if __name__ == '__main__':
    assert(False)
