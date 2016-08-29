#!/usr/bin/env python
import sys
l = -1
while True:
	b = sys.stdin.read(1)
	if b == '':
		sys.exit(0)
	i = ord(b)
	for v in range(7,-1,-1):
		x = int((i&(1<<v)) != False)
		if x != l:
			sys.stdout.write('%d' % ((i&(1<<v)) != False))
			sys.stdout.flush()
			l = x
