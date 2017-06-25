#!/usr/bin/env python
'''
This is a script configures and MEF service on an MRV devices.
1.  The Configuration Service CLI is generated based on parameters provided.
2.  The Configuration change is saved and then pushed to the device.
 
INPUT FILES
   mrv_files.yml2
OUTPUT FILES
   mrv_service_SERVICE-NAME-Date.cfg
'''
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
    '''Establish Netmiko SSH connection; print device prompt.'''
    try:
        print("\n")
        print('-' * 40)
        print(netmiko_dict)
        print("Establish SSH Conn: {}".format(device_name))
        netmiko_dict['password'] = PASSWORD
        net_connect = ConnectHandler(**netmiko_dict)
        print(net_connect.send_command("show arp"))
        print(net_connect.find_prompt())
        print(net_connect.send_command("show run"))
        print(net_connect.config_mode())
        config_commands = 'interface Vlan1 \n ip address 10.1.1.1 255.255.255.0'
        print(net_connect.send_config_set(config_commands))
        print('-' * 40)
        print("\n")
    except NetMikoAuthenticationException:
        print("SSH login failed")

def build_jinja2_template(template_file,my_vars):
    '''   Biuld the configuration by Rendering a Jinja2 configuration file  '''
    with open(template_file) as f1:
        cfg_template =  f1.read()
    f1.close()
    print ("cfg_template {} ".format(cfg_template))
    template_j2 = jinja2.Template(cfg_template)
    cfg_output = (template_j2.render(my_vars))
    print (cfg_output)
    return cfg_output




#def main():
'''Make it so '''

### Read the Master Files 
### Master files determines all the files needed to execute successfully"
master_file = "mrv_files.yml"
with open(master_file) as mf:
    master = yaml.load(mf)        
mf.close()
print (master)

### From the Master file read service variables.   These variables fully define the service to be configured
with open(master['service_vars']) as tf:
    my_vars = yaml.load(tf)
tf.close()
print (my_vars)


### *******  Build the configuration **********
cfg_output = build_jinja2_template(master['template_file'],my_vars)


# *******   Output the configuration to a file.   For audit purposes ***** 
mrv_service_file = 'mrv_service_' + my_vars['service_name'] + '_' + date.isoformat(date.today()) +'.cfg'
print (mrv_service_file)
with open(mrv_service_file,'w') as f3:
     cfg_file = f3.write(cfg_output)  
f3.close()

#   Read a CSV file. Use the first line as a header line. Return a dictionary.
#    establish a Netmiko SSH connection using the CSV file
# *******   Output the configuration to a file ***** 
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
         break
f2.close()
print(read_csv)

#for entry in read_csv:
#     device_name = entry.pop('device_name')
#     print (device_name)
#     establish_netmiko_conn(device_name, entry)


#if __name__ == "__main__":
#    main()
