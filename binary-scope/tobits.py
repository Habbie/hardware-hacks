#!/usr/bin/env python
import sys
while True:
	b = sys.stdin.read(1)
	if b == '':
		sys.exit(0)
	i = ord(b)
	for v in range(7,-1,-1):
		sys.stdout.write('%d' % ((i&(1<<v)) != False))
	
