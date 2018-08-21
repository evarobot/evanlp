#!/usr/bin/env python
# encoding: utf-8

import json
import requests


def test_question(data):
    params = {
        'robotid': '12345',
        'appname': 'Maccaw',
        'data': data,
        'version': 0.1
    }
    axm_qa_service = 'http://192.168.0.30:7000/viki/recommend'
    headers = { 'content-type': 'application/json' }
    v =  json.dumps(params).encode('utf8')
    data = requests.post(axm_qa_service, data=v,
                        headers=headers, timeout=2).text
    return json.loads(data)


if __name__ == '__main__':
    data = {
        'sex': 'male',
        'age': 56,
        'with_kid': True
    }
    ret = test_question(data)
    if 'error' in ret:
        print ret['error']
    else:
        print ret
