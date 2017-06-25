#!/usr/bin/env python
"""
INPUT FILES
   mrv_files.yml2
OUTPUT FILES
   mrv_service_SERVICE-NAME-Date.cfg
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
import yaml
from pprint import  pprint
from datetime import date

PASSWORD = getpass()

def establish_netmiko_conn(device_name, netmiko_dict):
# USE Netmiko to connect to the device
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

def build_jinja2_template(template_file,my_vars):
#   Biuld the configuration by Rendering a Jinja2 configuration file
    with open(template_file) as f1:
        cfg_template =  f1.read()
    f1.close()
    print ("cfg_template {} ".format(cfg_template))
    template_j2 = jinja2.Template(cfg_template)
    cfg_output = (template_j2.render(my_vars))
    print (cfg_output)
    return cfg_output




#def main():
##### Read the Master Files #####
##### Master files determines all the files needed to execute successfully"
master_file = "mrv_files.yml"
with open(master_file) as mf:
    master = yaml.load(mf)        
mf.close()
print (master)

##### From the Master file read service variables.   These variables fully define the service to be configured
with open(master['service_vars']) as tf:
    my_vars = yaml.load(tf)
tf.close()
print (my_vars)


# *******  Build the configuration **********
cfg_output = build_jinja2_template(master['template_file'],my_vars)


#Read a CSV file. Use the first line as a header line. Return a dictionary."""5yy

#    Expand on exercise1 except establish a Netmiko SSH connection using the CSV file
# *******   Output the configuration to a file ***** 
mrv_service_file = 'mrv_service_' + my_vars['service_name'] + '_' + date.isoformat(date.today()) +'.cfg'
print (mrv_service_file)
with open(mrv_service_file,'w') as f3:
     cfg_file = f3.write(cfg_output)  
f3.close()

print (master['mrv_device'])
with open(master['mrv_device']) as f2:
     read_csv = csv.DictReader(f2)
     for row in read_csv:
         print (', '.join(row))
       #  print (row.pop('device_name'))
         print (row)
         print (dir(row))
         print (type(row))
         device_name = row.pop('device_name')
         establish_netmiko_conn(device_name, row)
f2.close()
print(read_csv)

#for entry in read_csv:
#     device_name = entry.pop('device_name')
#     print (device_name)
#     establish_netmiko_conn(device_name, entry)


#if __name__ == "__main__":
#    main()
