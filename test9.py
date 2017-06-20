#!/usr/bin/env python
f = open("show_version.txt")
lines = f.readlines()
for line in lines:
    if 'Processor board ID' in line:
        print ("\n SN {}".format(line.split("Processor board ID")[1]))
