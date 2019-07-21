#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import interface

lhost = "127.0.0.1"
lport = 8888
key = 16
import server
c2c = server.Server(lhost, lport, 16)
