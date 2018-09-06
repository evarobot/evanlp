#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy

from vikinlu.robot import NLURobot

app = Flask(__name__)


class _Config(object):
    """"""

    log_level = "INFO"
    log_path = "/Users/bitmain/logs/NLU/"

    SECRET_KEY = "a0c23007-f1c0-11e7-b62a-c8e0eb182c79"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/CMS"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


Config = _Config()


app.config.from_object(Config)
db = SQLAlchemy()


@app.route("/v2/nlu/<domain_id>/predict", methods=["GET", "POST"])
def predict(domain_id):
    robot = NLURobot.get_robot(domain_id)
    data = json.loads(request.data)
    ret = robot.predict(data["context"], data["question"])
    return jsonify(ret)


@app.route("/v2/nlu/<domain_id>/train", methods=["GET", "POST"])
def train(domain_id):
    robot = NLURobot.get_robot(domain_id)
    ret = robot.train(("logistic", "0.1"))
    return jsonify(ret)


if __name__ == '__main__':
    db.init_app(app)
    app.run()
