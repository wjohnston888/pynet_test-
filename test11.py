from __future__ import print_function
from pprint import pprint
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


