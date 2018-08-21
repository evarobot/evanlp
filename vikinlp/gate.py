#!/usr/bin/env python
# encoding: utf-8
import requests
import json


cms_host = "http://192.168.0.30"
cms_port = 8887


class RPCServiceGate(object):
    """"""
    def __init__(self, service):
        self.service = service

    def get_label_data(self, domain_name):
        return self.service.get_label_data(domain_name)

    def get_domain(self, domain_id):
        return self.service.get_domain(domain_id)

    def get_all_domains(self, type_):
        return self.service.get_all_domains(type_)

    def get_domain_slots(self, domain_id):
        return self.service.get_domain_slots(domain_id)

    def get_domain_values(self, domain_id, type_):
        return self.service.get_domain_values(domain_id, type_)

    def get_intent(self, intent_id):
        return self.service.get_intent(intent_id)

    def get_domain_intents(self, domain_id):
        return self.service.get_domain_intents(domain_id)

    def get_intent_slots(self, intent_id):
        return self.service.get_intent_slots(intent_id)


class HttpServiceGate(object):
    def __init__(self):
        pass

    def get_label_data(self, domain_name):
        url = u'{0}:{1}/v2/{2}/label_data'.format(
            cms_host, cms_port, domain_name)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_domain(self, domain_id):
        url = '{0}:{1}/v2/domains/{2}'.format(cms_host, cms_port, domain_id)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_all_domains(self, type):
        url = '{0}:{1}/v2/domains'.format(cms_host, cms_port)
        ret = requests.get(url, data=json.dumps({"type": type}))
        return json.loads(ret.text)

    def get_domain_slots(self, domain_id):
        url = '{0}:{1}/v2/{2}/slots'.format(cms_host, cms_port, domain_id)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_domain_values(self, domain_id, type_):
        url = '{0}:{1}/v2/{2}/values?type={3}'.format(
            cms_host, cms_port, domain_id, type_)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_intent(self, intent_id):
        url = '{0}:{1}/v2/intents/{2}'.format(cms_host, cms_port, intent_id)
        ret = requests.get(url)
        return json.loads(ret.text)

    def get_domain_intents(self, domain_id):
        url = '{0}:{1}/v2/{2}/intents'.format(cms_host, cms_port, domain_id)
        ret = requests.get(url)
        return json.loads(ret.text)


try:
    from evecms.services.service import EVECMSService, connect_db
    connect_db()
except ImportError as e:
    data_gate = HttpServiceGate()
else:
    service = EVECMSService()
    data_gate = RPCServiceGate(EVECMSService())

__all__ = ['data_gate']
