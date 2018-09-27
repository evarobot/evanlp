#!/usr/bin/env python
# encoding: utf-8

import logging
import helper

from evecmsweb.app import setup_app
from vikicommon.log import init_logger
from vikinlu.config import ConfigMongo
from vikinlu.filters import Sensitive
from vikinlu.robot import NLURobot
from vikinlu.util import cms_rpc
from vikinlu.model import clear_intent_question, connect_db
from evecms.models import (
    Domain
)

app = setup_app()
app.app_context()

init_logger(level="DEBUG", path="./")
log = logging.getLogger(__name__)
dm_robot_id = "12345"

connect_db(dbname=ConfigMongo.database,
           host=ConfigMongo.host,
           port=ConfigMongo.port)
log.info('连接Mongo: IP-{0} DB-{1}'.format(
    ConfigMongo.host, ConfigMongo.database))


def test_sensitive():
    domain = Domain.query.filter_by(name="A").first()
    sensitive = Sensitive.get_sensitive(str(domain.id))
    assert(set(sensitive._words) == set([u"共产党", u"毛泽东"]))
    assert(sensitive.detect(u'共产党万岁') == True)
    assert(sensitive.detect(u'你叫什么') == False)


def test_integration_train():
    domain = Domain.query.filter_by(name="A").first()
    robot = NLURobot.get_robot(str(domain.id))
    robot.train(("logistic", "0.1"))
    label_data = cms_rpc.get_tree_label_data(str(domain.id))
    helper.assert_intent_question(str(domain.id), label_data)


clear_intent_question("C")



# TODO: casual talk test

if __name__ == '__main__':
    assert(False)
