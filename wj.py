#!/usr/bin/env python
"""
INPUT FILES
   wj.j2
   wj.parameters
OUTPUT FILES
   wj.cfg
This script takes a Jinja2 file combined with appropriate parameters and generates the MRV Servcie CLI code
The script then connects to the device supplied in the parameters using Netmiko
Currently this script works for e-line
"""
from __future__ import print_function
from __future__ import unicode_literals
import csv
from getpass import getpass
from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
import csv
import jinja2
from pprint import  pprint

PASSWORD = getpass()

def establish_netmiko_conn(device_name, netmiko_dict):
    """Establish Netmiko SSH connection; print device prompt."""
    try:
        print("\n")
        print('-' * 40)
        print("Establish SSH Conn: {}".format(device_name))
        netmiko_dict['password'] = PASSWORD
        net_conn = ConnectHandler(**netmiko_dict)
        print(net_conn.find_prompt())
        print('-' * 40)
        print("\n")
    except NetMikoAuthenticationException:
        print("SSH login failed")


def build_jinja2_template(template_file_name,my_vars):
#    print template.render(my_vars) 
#    return template.render(my_vars)
    with open(template_file) as f1:
        cfg_template =  f1.read()
    f1.close()
    print ("cfg_template {} ".format(cfg_template))
    template_j2 = jinja2.Template(cfg_template)
    cfg_output = (template_j2.render(my_vars))
    print (cfg_output)
    print (template.render(my_vars)) 
    return template.render(my_vars)

        

my_vars = {
    'service_name' : 'AXX00099999',
    'service_type' : 'port',
    'service_product' : 'e-line',
    'cbs_value' : 16384,
    's_vlan' : 234,
    'bandwidth_f1' : 2,
    'bandwidth_f2' : 20,
    'bandwidth_f3' : 200,
    'oam' : 'True',

}

#Read a CSV file. Use the first line as a header line. Return a dictionary."""

#def main():
##    """
#    Expand on exercise1 except establish a Netmiko SSH connection using the CSV file
#    information.
#    """
template_file = 'wj.j2'
out1 = build_jinja2_template(template_file,my_vars)

#with open(template_file) as f1:
#    cfg_template =  f1.read()
#f1.close()
#print ("cfg_template {} ".format(cfg_template)) 
#template_j2 = jinja2.Template(cfg_template)
#cfg_output = (template_j2.render(my_vars)) 
#print (cfg_output)   
#    return template.render(my_vars)

#pprint(template_j2)
connect_file = 'wj.cfg'
with open('connect_file','w') as f3:
     cfg_file = f3.write(cfg_output)  

file_name = "wj.csv"
with open(file_name) as f2:
     read_csv = csv.DictReader(f2)
for entry in read_csv:
     device_name = entry.pop('device_name')
     establish_netmiko_conn(device_name, entry)


#if __name__ == "__main__":
#    main()
