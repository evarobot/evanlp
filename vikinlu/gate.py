#!/usr/bin/env python
# encoding: utf-8
import requests
import json

from vikinlu.config import ConfigData


class HttpServiceGate(object):
    def __init__(self):
        self._host = ConfigData.data_server_host
        self._port = ConfigData.data_server_port

    def get_label_data(self, domain_name):
        url = u'{0}:{1}/v2/{2}/label_data'.format(
            self._host, self._port, domain_name)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_domain(self, domain_id):
        url = '{0}:{1}/v2/domains/{2}'.format(self._host, self._port, domain_id)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_all_domains(self, type):
        url = '{0}:{1}/v2/domains'.format(self._host, self._port)
        ret = requests.get(url, data=json.dumps({"type": type}))
        return json.loads(ret.text)

    def get_domain_slots(self, domain_id):
        url = '{0}:{1}/v2/{2}/slots'.format(self._host, self._port, domain_id)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_domain_values(self, domain_id, type_):
        url = '{0}:{1}/v2/{2}/values?type={3}'.format(
            self._host, self._port, domain_id, type_)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_intent(self, intent_id):
        url = '{0}:{1}/v2/intents/{2}'.format(self._host, self._port, intent_id)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_domain_intents(self, domain_id):
        url = '{0}:{1}/v2/{2}/intents'.format(self._host, self._port, domain_id)
        ret = requests.get(url)
        return json.loads(ret.text)


data_gate = HttpServiceGate()
__all__ = ['data_gate']
