#!/usr/bin/env python
'''
This is a script configures and MEF service on MRV devices.
1.  The Configuration Service CLI is generated based on parameters provided.
2.  The Configuration change is saved and then pushed to the device.
 
INPUT FILES
   mrv_files.yml
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
import re
import sys
import fileinput
reload (sys)
sys.setdefaultencoding('utf8')

PASSWORD = getpass()

def establish_netmiko_conn(device_name, netmiko_dict, verbose=True):
    '''Establish Netmiko SSH connection; print device prompt.'''
    try:
#        print("\n")
#        print('-' * 40)
#        print(netmiko_dict)
#        print("Establish SSH Conn: {}".format(device_name))
        netmiko_dict['password'] = PASSWORD
        net_connect = ConnectHandler(**netmiko_dict)
        net_connect.enable()
        show_version = net_connect.send_command("show ethernet oam ccm")
        print(show_version)
        if device_name == "clgrab42mmmef002":
            rout1 = net_connect.send_config_set("ethernet oam domain 2 \n service 123 \n show rmeps")
            print (rout1)
        else:
            rout1 = net_connect.send_config_set("provision \n service EP-LAN-cert  \n show rmeps")
            print (rout1)
            
#        reg1 = re.search('MasterOS version........',show_version)
#        reg2 = re.search('FPGA version......|CPLD-2000 version.....',show_version)
#        print("",device_name,",", reg1.group(0),",",reg2.group(0),"")
#        print(reg1.group(0))
#        print(reg2.group(0))
#        print(net_connect.find_prompt())
#        print(net_connect.send_command("show run"))
#        print('Attempting config mode')
#        print(net_connect.config_mode())
#        print('Attempting to upload config changes')
#        print(net_connect.send_config_from_file(config_file))
#        config_commands = 'write mem'
#        print re.search('Version.,show_version)
#        print (reg1)
#	print(device_name,'configuration changed')
#        config_commands = 'do ping 1.1.1.1'
#        print(net_connect.send_config_set(config_commands))
#        print('\n 6. Verifying configuration and Service \n')
#        print(net_connect.send_config_set("provision \n service " + service_name + " \n show config"))
#        ccm_test = net_connect.send_config_set(" \n service " + service_name + "\n show ccm \n")
#        print(net_connect.check_enable_mode())
#        print(net_connect.check_config_mode())
#        ccm_test = net_connect.send_config_set(" provision \n service " + service_name  + " \n show ccm \n",delay_factor=3)
# 
#        if (ccm_test.split()[24] == 'Up'):
#              print ('#' * 40)
#              print ('Test Successful, service link established')
#              print ('MAC address is up')
#              print ('#' * 40)
#        else: 
#              print ('Link not established')
#        print(ccm_test)
#        mos_command = 'ping ' + test_ip
#        ping_response = net_connect.send_command(mos_command)
#        print(ping_response)
#        if (ping_response.find('bytes from') != -1):
#            print ('#' * 40)
#            print ("Successful Ping")
#            print ('#' * 40)
#        else:
#            print ("Not Connected yet")
#        print(ccm_test.split())
#        print('*****#24#----',ccm_test.split()[24],'----####****')
#        print('*****#25#----',ccm_test.split()[25],'----####****')
#        print('*****#26#----',ccm_test.split()[26],'----####****')
#        print('*****#27#----',ccm_test.split()[27],'----####****')
#        print('*****#28#----',ccm_test.split()[28],'----####****')
#        print("\n")
    except NetMikoAuthenticationException:
        return ("SSH login failed")





#def main():
'''Make it so '''

### Read the Master Files 
### Master files determines all the files needed to execute successfully"
master_file = "mrv_files.yml"
with open(master_file) as mf:
    master = yaml.load(mf)        
mf.close()
#print ('\n 1. Read Master Files ')
#pprint (master)


#   Read a CSV file. Use the first line as a header line. Return a dictionary.
#    establish a Netmiko SSH connection using the CSV file
# *******   Output the configuration to a file ***** 
#print (master['mrv_device'])
print ("SOAM ")
with open(master['mrv_device']) as f2:
     read_csv = csv.DictReader(f2)
     j = 1
     for row in read_csv:
     ### From the Master file read service variables.   These variables fully define the service to be configured
#         service_vars_file = master['service_vars'].split('.')[0] + str(j) +'.' + master['service_vars'].split('.')[1]
#         print(j)
#         print (service_vars_file)
#         with open(service_vars_file) as tf:
#             my_vars = yaml.load(tf)
#         tf.close()
#         print ('\n 2. Read in Service Varirables')
#         if 'mtu_size' not in my_vars.keys():
#             my_vars['mtu_size'] = 2004
#         my_vars['cbs_1'] = int(calc_cbs(my_vars['bandwidth_f1'],my_vars['mtu_size']))
#
#         #print ('\n 3. Built the configuration based on the Jinja2 template')
         device_name = row.pop('device_name')
         print ("\n\n",device_name)
         # *******   Output the configuration to a file.   For audit purposes ***** 
#         mrv_service_file = 'mrv_service_' + my_vars['service_name'] + '-' + device_name + '-' + date.isoformat(date.today()) + '-' + str(j) + '.cfg'
#         print ('\n 4. Created Audit file is:', mrv_service_file)
#         with open(mrv_service_file,'w') as f3:
#              cfg_file = f3.write(cfg_output)  
#         f3.close()
         command_output = establish_netmiko_conn(device_name, row )
         if command_output == "SSH login failed":
             print ("Bad Password exiting")
             break
         j += 1
#         print (j,"end for")
         #            break
f2.close()
#print(read_csv)



#if __name__ == "__main__":
#    main()
