#!/usr/bin/env python
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from getpass import getpass

USER = "pyclass"
PASSWD = getpass()



my_vars = {
   'juniper1':
       'management_ip': 
       'ge_0_0_0_2_ip': '10.10.10.1',
       'ge_0_0_0_2_mask': '24', 
       'local_as': '101',
       'peer_as': '102',
       'peer_ip': '10.10.10.2',
   'juniper2':
       { 'ge_0_0_0_2_ip': '10.10.10.22,
       'ge_0_0_0_2_mask': '24', 
       'local_as': '101',
       'peer_as': '102',
       'peer_ip': '10.10.10.2',

      },
}
juniper_srx = {
    "host": "184.105.247.76",
    "user": "pyclass",
    "password": getpass(),
}

Connecting to device
host = router_id['management_ip']
a_device = Device(host,user=USER, password=PASSWD)
a_device.open()
a_device.timeout = 90
for router_id, router_vars in my_vars.items():
    template = jinja2.Template(bgp_templatej)
    rtr_cfg - template.render(my_vars['juniper1'])
    print(rtr_cfg)
    print("This is router: {}".format(router_id))

a_device.timeout = 90
cfg = Config(a_device)

template_file = 'build.j2'
with open(template_file) as f:
    bgp_template = f.read()


print "Setting hostname using set notation"
cfg.load("set system host-name test1", format="set", merge=True)

print "Current config differences: "
print cfg.diff()

print "Performing rollback"
cfg.rollback(0)

print "\nSetting hostname using {} notation (external file)"
cfg.load(path="load_hostname.conf", format="text", merge=True)

print "Current config differences: "
print cfg.diff()

print "Performing commit"
cfg.commit()

print "\nSetting hostname using XML (external file)"
cfg.load(path="load_hostname.xml", format="xml", merge=True)

print "Current config differences: "
print cfg.diff()

print "Performing commit"
cfg.commit()
print
