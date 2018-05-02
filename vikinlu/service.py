# -*- coding: utf-8 -*-

import logging
from vikinlu.robot import NLURobot

log = logging.getLogger(__name__)


class NLUService:

    name = "nlu_service"

    def predict(self, dm_robot, domain_id, question):
        log.debug("-------------------- predict: %s" % question)
        robot = NLURobot.get_robot(domain_id)
        return robot.predict(dm_robot, question)

    def train(self, domain_id, algorithm):
        log.debug("-------------------- train: %s" % domain_id)
        robot = NLURobot.get_robot(domain_id)
        return robot.train(algorithm)
