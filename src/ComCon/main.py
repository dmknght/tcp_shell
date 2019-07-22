#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

try:
	_, lhost, lport, key = sys.argv
	lport, key = int(lport), int(key)
	import server
	c2c = server.Server(lhost, lport, key)
except ValueError:
	print("%s <lhost> <lport> <xor key (int)>" %(sys.argv[0]))
except Exception as error:
	print("[x] Error: %s" %(error))
