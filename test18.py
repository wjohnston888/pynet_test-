#!/usr/bin/env python
from __future__ import print_function
from __future__ import unicode_literals
from pprint import pprint
import re

class NetDevice(object):
    def __init__(self, ip_addr, username, password):
        self.ip_addr = ip_addr
        self.username = username
        self.password = password

        self.serial_number = ''
        self.vendor = ''
        self.model = ''
        self.os_version = ''
        self.uptime = ''



    def print_ip(self):
        print("Device IP address is: {}".format(self.ip_addr))

    def print_credentials(self):
        print("Device username: {}".format(self.username))
        print("Device password: {}".format(self.password))

    def set_vendor(self, vendor):
        self.vendor = vendor
        print("Setting vendor to: {}".format(self.vendor))


if __name__ == "__main__":

    print()
    # Validation code
    my_obj1 = NetDevice(ip_addr='1.1.1.1', username='admin', password='pwd')
    my_obj1.print_ip()
    my_obj1.print_credentials()
    my_obj1.set_vendor("Cisco")
    print()





def my_func(x,y,z):
    print(x,y,z)
    return x+y+z


def read_file(filename):
    with open(filename) as f:
        return f.read()

def find_sn(input_str):
    for line in input_str.splitlines():
        if 'Processor board ID' in line:
            sn = (line.split("Processor board ID")[1])
            return sn.strip()

my_obj1 = NetDevice(ip_addr='1.1.1.1', username='admin', password='pwd')
my_obj2 = NetDevice(ip_addr='1.1.1.2', username='admin', password='pwd')
my_obj3 = NetDevice(ip_addr='1.1.1.3', username='admin', password='pwd')
my_obj4 = NetDevice(ip_addr='1.1.1.4', username='admin', password='pwd')
pprint (my_obj1)
pprint (my_obj2)
pprint (my_obj3)
pprint (my_obj4)


filename = "show_version.txt"
my_device = {}

show_ver = read_file(filename)
my_device['serial_number'] = find_sn(show_ver)
print()
pprint(my_device)
print()

my_func(x=10,y=17,z=3)
my_list = [3,4,5]
output = my_func(*my_list)
my_dict = {
    'x': 22,
    'y': 7,
    'z': 8
    }
output2 = my_func(**my_dict)

f = open("show_int_fa4.txt")
lines = f.read()
f.close()

match1 = re.search(r"(\d+) packets input, (\d+) bytes", lines)    
match2 = re.search(r"(\d+) packets output, (\d+) bytes", lines)    
packets_in = match1.group(0)
packets_out = match2.group(0)
print (packets_in,packets_out)


f = open("show_mac_multicast.txt")
lines = f.read()
f.close()
match1 = re.search(r"(\d+) packets input, (\d+) bytes", lines)

my_device = {}
my_device['ip_addr'] = '1.2.3.4'
my_device['username'] = 'wjohnston'
my_device['password'] = 'password1'
my_device['vendor'] = 'juniper'
my_device['model'] = 'MX480'
for key,val in my_device.items():
    print (key,val)
my_device['password'] = 'NewPass#32'
my_device['secret'] = 'dont tell' 
bad_device = my_device.get('whatever','bad stuff')
print (bad_device)

# re.search(r"^\*",line)
#match = re.search(r"^\Cisco IOS So.* Version (.*) ",line)
#match.group(0)
#match.group(1) 



