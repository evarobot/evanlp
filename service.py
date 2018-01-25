# -*- coding: utf-8 -*-

from nameko.rpc import rpc


class NLUService:

    name = "nlu_service"

    @rpc
    def say_hello(self, name):
        return "hello aa %s" % name
