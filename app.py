#!/usr/bin/env python
# encoding: utf-8
import json
import logging
from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_mongoengine import MongoEngine

from vikicommon.log import init_logger
from vikinlu.config import ConfigLog
from vikinlu.config import ConfigApps, ConfigMongo
from vikinlu.robot import NLURobot

app = Flask(__name__)


app.config.from_object(ConfigMongo)
app.config.from_object(ConfigApps)
db = SQLAlchemy()
mongodb = MongoEngine()
init_logger(level=ConfigLog.log_level, path=ConfigLog.log_path)
log = logging.getLogger(__name__)


@app.route("/v2/nlu/<domain_id>/predict", methods=["GET", "POST"])
def predict(domain_id):
    robot = NLURobot.get_robot(domain_id)
    data = json.loads(request.data)
    ret = robot.predict(data["context"], data["question"])
    return jsonify(ret)


@app.route("/v2/nlu/<domain_id>/train", methods=["GET", "POST"])
def train(domain_id):
    """
    Parameters
    ----------
    algorithm : str, Algorithm name.

    Returns
    -------
    {
        "code": 0,

        "data": {

            "intents": [

                "label": 意图标识,

                "count": 问题数量,

                "precise": 准去率,

            ]

            "total_prciese": 业务准确率

        }

    }
    """
    data = json.loads(request.data)
    robot = NLURobot.get_robot(domain_id)
    ret = robot.train(("logistic", "0.1"))
    log.info("TRAIN ROBOT: {0}".format(data["project"]))
    return jsonify({
        "code": 0,
        "data": ret
    })


@app.route("/v2/nlu/<domain_id>/reset", methods=["GET", "POST"])
def reset(domain_id):
    data = json.loads(request.data)
    robot = NLURobot.get_robot(domain_id)
    robot.reset_robot()
    log.info("RESET ROBOT: {0}".format(data["project"]))
    return jsonify({
        "code": 0
    })


if __name__ == '__main__':
    db.init_app(app)
    mongodb.init_app(app)
    app.run()
