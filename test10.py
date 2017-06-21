from __future__ import print_function
from pprint import pprint
f = open("show_ip_bgp.txt")
output = f.readlines()
my_dict = {}

for line in output:
    line2 = line.strip()
    if line2 and line2[0] == '*':
       fields =  line.split()
       prefix = fields[1]
       as_path = fields[5:-1]
       print (prefix,as_path)
