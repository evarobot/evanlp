# -*- coding: utf-8 -*-

from vikinlu.robot import NLURobot


class NLUService:

    name = "nlu_service"
    robots = {}

    def _get_robot(self, domain_id):
        robot = self.robots.get(domain_id, None)
        if robot:
            return robot
        robot = NLURobot.get_robot(domain_id)
        self.robots[domain_id] = robot
        return robot

    def predict(self, domain_id, question):
        robot = self._get_robot(domain_id)
        return robot.predict(question)

    def train(self, domain_id, algorithm):
        robot = self._get_robot(domain_id)
        return robot.train(algorithm)
