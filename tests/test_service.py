#!/usr/bin/env python
# encoding: utf-8

from nameko.standalone.rpc import ClusterRpcProxy

with ClusterRpcProxy({"AMQP_URI": "pyamqp://guest:guest@localhost"}) as rpc:
    result = rpc.nlu_service.say_hello("world")
    print(result)
