# encoding: utf-8

import os
#from django.conf import settings


def init():
    #settings.configure()
    pass


class DataConfig(object):
    """"""
    nlp_data_path = './'


class ConfigLog(object):
    log_level = 'INFO'
    log_to_file = True
    log_to_console = False
    log_path = './'
