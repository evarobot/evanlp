#!/usr/bin/env python
# encoding: utf-8
import evecms.tests.mongo_helper as db
from evecms.services.service import EVECMSService
import logging
log = logging.getLogger(__name__)


def generate_nlu_data():
    service = EVECMSService()

    domain_c = db.create_domain({
        "name": "C",
        "version": "0.1",
        "is_skill": False
    })
    service.add_filterword(domain_c, "共产党")
    service.add_filterword(domain_c, "毛泽东")
    service.add_filterword(domain_c, "法轮功")

    db.create_value({
        "domain_id": "C",
        "name": u"今天",
        "words": ["当日"]
    })

    db.create_value({
        "domain_id": "C",
        "name": u"明天",
        "words": ["明儿"]
    })

    db.create_slot({
        "domain_id": "C",
        "name": u"日期",
        "values": [u"今天", u"明天"]
    })

    db.create_slot({
        "domain_id": "C",
        "name": u"城市",
        "values": [u"深圳", u"上海"]
    })

    db.create_slot({
        "domain_id": "C",
        "name": u"location",
        "values": [u"周黑鸭", u"耐克"]
    })

    db.create_qa({
        "domain_id": "C",
        "title": "你叫什么名字",
        "intent": "name.query",
        "slots": [],
        "subject": "主题",
        "scope": "可见域",
        "answer_type": "query",
        "std_template": "你叫什么名字",
        "question_templates": [
            {
                "template": "你叫什么名字",
                "create_datetime": "2018-01-01 12:00:00"
            },
            {
                "template": "你的姓名是什么",
                "create_datetime": "2018-01-01 12:00:00"
            },
        ],
        "questions": [],
        "answer_items": [
            {
                "event_id": "name_query",
                "key": {},
                "answer": {
                    "tts": [
                        {
                            "text": u"小莫",
                            "create_datetime": "2018-01-01 12:00:00"
                        }
                    ],
                    "web": {
                        "text": u"界面上显示的文字"
                    }
                }
            }
        ]
    })

    db.create_qa({
        "domain_id": "C",
        "title": "地点问询",
        "intent": "where.query",
        "slots": ["location"],
        "subject": "主题",
        "scope": "可见域",
        "answer_type": "query",
        "std_template": "<location>怎么走",
        "question_templates": [
            {
                "template": "<location>怎么走",
                "create_datetime": "2018-01-01 12:00:00"
            },
            {
                "template": "<location>在哪里",
                "create_datetime": "2018-01-01 12:00:00"
            },
        ],
        "questions": [
            "耐克怎么走?"
            "美国耐克怎么走?"
            "周黑鸭怎么?"
            "鸭鸭怎么走?"
        ],
        "answer_items": [
            {
                "event_id": "nike",
                "key": {
                    "location": {
                        "name": "耐克",
                        "words": ["美国耐克"]
                    },
                },
                "answer": {
                    "tts": [
                        {
                            "text": u"左边走",
                            "create_datetime": "2018-01-01 12:00:00"
                        },
                    ],
                    "web": {
                        "text": u"界面上显示的文字2"
                    }
                }
            },
            {
                "event_id": "zhou_hei_ya",
                "key": {
                    "location": {
                        "name": "周黑鸭",
                        "words": ["鸭鸭", "周黑"]
                    },
                },
                "answer": {
                    "tts": [
                        {
                            "text": u"直走",
                            "create_datetime": "2018-01-01 12:00:00"
                        },
                    ],
                    "web": {
                        "text": u"界面上显示的文字2"
                    }
                }
            }
        ]
    })


if __name__ == '__main__':
    db.clear_all()
    generate_nlu_data()
