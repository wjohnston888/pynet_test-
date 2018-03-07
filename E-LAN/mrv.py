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
from lxml import etree
from xml.etree import ElementTree
#from lxml import raiseParseError
import csv
import jinja2
import yaml
from pprint import  pprint
from datetime import date
import re
import string
import repr
import sys
import fileinput
from jnpr.junos.device import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
from jnpr.junos.rpcmeta import _RpcMetaExec
import jxmlease
from ciscoconfparse import CiscoConfParse
import os, errno
import time
import socket
import xmltodict


reload (sys)
sys.setdefaultencoding('utf8')

PASSWORD = getpass()

def establish_netmiko_conn(device_name, netmiko_dict, config_file, service_name,  verbose=True):
    '''Establish Netmiko SSH connection; print device prompt.'''
    try:
#        print("\n")
        print('-' * 40)
#        print(netmiko_dict)
#        netmiko_dict['global_delay_factor'] = 3
        print("Establish SSH Conn: {}".format(device_name))
        netmiko_dict['password'] = PASSWORD
        net_connect = ConnectHandler(**netmiko_dict)
        net_connect.enable()
#        print(net_connect.send_command("show arp"))
        print(net_connect.find_prompt())
#        print(net_connect.send_command("show run"))
        print('Attempting config mode')
        print(net_connect.config_mode())
        print('Attempting to upload config changes')
        print(net_connect.send_config_from_file(config_file))
#        config_commands = 'write mem'
#        print(net_connect.send_config_set(config_commands))
#	print(device_name,'configuration changed')
#        config_commands = 'do ping 1.1.1.1'
#        exit()
#        print(net_connect.send_config_set(config_commands))


    except NetMikoAuthenticationException:
        print("SSH login failed")


def test_service(device_name, netmiko_dict, config_file, service_name, my_vars, test_ip, verbose=True):
    '''Establish Netmiko SSH connection and test the service.'''
    try:
#        print("\n")
        print('-' * 40)
#        print(netmiko_dict)
#        netmiko_dict['global_delay_factor'] = 3
        print("Establish SSH Conn: {}".format(device_name))
        netmiko_dict['password'] = PASSWORD
        net_connect = ConnectHandler(**netmiko_dict)
        net_connect.enable()
#        print(net_connect.send_command("show arp"))
        print(net_connect.find_prompt())


        print('\n 6. Verifying configuration and Service \n')
        if (test_ip.split(".")[3] == "1"):
#            print(net_connect.send_config_set("provision \n service " + service_name + " \n show config"))
#            ccm_test = net_connect.send_config_set(" \n service " + service_name + "\n show ccm \n")
#        print(net_connect.check_enable_mode())
#        print(net_connect.check_config_mode())
#            ccm_test = net_connect.send_config_set(" provision \n service " + service_name  + " \n show ccm \n",delay_factor=3)
#            ccm_test = net_connect.send_config_set(" show ethernet oam ccm\n",delay_factor=3)
            ccm_test = net_connect.send_command("show ethernet oam ccm\n")
            rmep_cmd = "show ethernet oam domain "+ str(my_vars['oam_md']) + " service " + str(my_vars['oam_ma']) + " mep " + str(my_vars['mep_id']) + " rmeps"
#            rmep_cmd = "show ethernet oam domain "+ my_vars['oam_md'] + " service " + my_vars['oam_ma'] + " mep " + my_vars['mep_id'] + " rmeps"

            #print ("ccm test = ",ccm_test.find(" Up ")) 
            #print ("ccm test = ",ccm_test.find(" Dn "))
            
            if (ccm_test.find(" Up ") != -1):
                  print ('#' * 40)
                  print ('Test Successful, Service OAM link established, Customer UNIs are inplace')
                  print ('MAC address is up')
                  print ('#' * 40)
            elif (ccm_test.find(" Dn ") != -1): 
                  print ('#' * 40)
                  print ('Test NOT Successful, Service OAM link NOT established')
                  print ("This may mean link between ENNI and NNI are in place but customer interface is down")
                  print ('#' * 40)
            else:
                  print ("Error ccm status not known")
            print(ccm_test)
            rmep_test = net_connect.send_command(rmep_cmd)
            if (rmep_test.find(" Up ") != -1):
                  print ('#' * 40)
                  print ('Test Successful, Service domain RMEPS links are established')
                  print ('MAC address is up')
                  print ('#' * 40)
            elif (rmep_test.find(" Dn ") != -1): 
                  print ('#' * 40)
                  print ('Test NOT Successful, Service OAM link NOT established')
                  print ("This may mean link between ENNI and NNI are in place but customer interface is down")
                  print ('#' * 40)
            else:
                  print ("Error ccm status not known")
            print(rmep_test)
            mos_command = 'ping ' + test_ip
            ping_response = net_connect.send_command(mos_command)
            print("\n",ping_response)
            if (ping_response.find('bytes from') != -1):
                print ('#' * 40)
                print ("Successful Ping, E-Access Connectivity between UNI and ENNI is in place")
                print ('#' * 40)
            else:
                print ("Not Connected yet")
#        print(ccm_test.split())
#        print('*****#24#----',ccm_test.split()[24],'----####****')
#        print('*****#25#----',ccm_test.split()[25],'----####****')
#        print('*****#26#----',ccm_test.split()[26],'----####****')
#        print('*****#27#----',ccm_test.split()[27],'----####****')
#        print('*****#28#----',ccm_test.split()[28],'----####****')
        print("\n")
    except NetMikoAuthenticationException:
        print("SSH login failed")

def calc_cbs(bandwidth,mtu=2004):
    '''    Calculate the CBS based on the bandwidth supplied '''
    bursttime = .005 # 5ms 
    cbs = bursttime * bandwidth * 1000000 /8
    if (cbs < mtu*8 and cbs != 0): # ensure CBS is atleast 8 times the MTU
        cbs = mtu*8
    #print(cbs)
    return int(cbs)

def build_jinja2_template(template_file,my_vars):
    '''   Biuld the configuration by Rendering a Jinja2 configuration file  '''
    with open(template_file) as f1:
        cfg_template =  f1.read()
    f1.close()
#    print ("cfg_template {} ".format(cfg_template))
    template_j2 = jinja2.Template(cfg_template)
    cfg_output = (template_j2.render(my_vars))
    cfg_output2 = "".join([s for s in cfg_output.strip().splitlines(True) if s.strip("\r\n").strip()])
    print (cfg_output2)
#    print ('Built Config based on Jinja2 Template',template_file)
    return cfg_output2




#def main():
'''Make it so '''

### Read the Master Files 
### Master files determines all the files needed to execute successfully"
master_file = "mrv_files.yml"
with open(master_file) as mf:
    master = yaml.load(mf)        
mf.close()
print ('\n 1. Read Master Files ')
pprint (master)


#   Read a CSV file. Use the first line as a header line. Return a dictionary.
#    establish a Netmiko SSH connection using the CSV file
# *******   Output the configuration to a file ***** 
#print (master['mrv_device'])
with open(master['mrv_device']) as f2:
     read_csv = csv.DictReader(f2)
     j = 1
     for row in read_csv:
     ### From the Master file read service variables.   These variables fully define the service to be configured
         service_vars_file = master['service_vars'].split('.')[0] + str(j) +'.' + master['service_vars'].split('.')[1]
         print(j)
         print (service_vars_file)
         with open(service_vars_file) as tf:
             my_vars = yaml.load(tf)
         tf.close()
         print ('\n 2. Read in Service Varirables')
         if 'mtu_size' not in my_vars.keys():
             my_vars['mtu_size'] = 2004
         if 'cbs_1' in my_vars.keys():
             my_vars['cbs_1'] = int(calc_cbs(my_vars['bandwidth_f1'],my_vars['mtu_size']))
         if 'cbs_2' in my_vars.keys():
             my_vars['cbs_2'] = int(calc_cbs(my_vars['bandwidth_f2'],my_vars['mtu_size']))
         if 'cbs_3' in my_vars.keys():
             my_vars['cbs_3'] = int(calc_cbs(my_vars['bandwidth_f3'],my_vars['mtu_size']))
         if 'cbs_4' in my_vars.keys():
             my_vars['cbs_4'] = int(calc_cbs(my_vars['bandwidth_f4'],my_vars['mtu_size']))
             
         pprint (my_vars)
         

         ### *******  Build the configuration for MRV **********
         print(master['mrv_template_file'])
         
         print ('\n 3a. Built the MRV configuration based on the Jinja2 template')
         device_name = row.pop('device_name')
         my_vars['mrv_device'] = device_name
         print("calling cfg=output = build_jinja2_template",master['pe_template_file'],my_vars)
         
         cfg_output = build_jinja2_template(master['mrv_template_file'],my_vars)
         # *******   Output the configuration to a file.   For audit purposes ***** 
         mrv_service_file = my_vars['service_name'] + '-mrv-' + device_name + '-' + date.isoformat(date.today()) + '-' + str(j) + '.cfg'
         print ('\n 3b. Created MRV Audit file is:', mrv_service_file)
         with open(mrv_service_file,'w') as f3:
              cfg_file = f3.write(cfg_output)  
         f3.close()

         ### *******  Build the configuration for PE **********
         print(master['pe_template_file'])
         print("calling cfg=output = build_jinja2_template",master['mrv_template_file'],my_vars)
         #my_vars['pe_device'] = my_vars['PE']
         cfg_output_pe = build_jinja2_template(master['pe_template_file'],my_vars)
         print ('\n 3c. Built the configuration PE based on the Jinja2 template')
         
         # *******   Output the configuration to a file.   For audit purposes ***** 
         pe_service_file =  my_vars['service_name'] + '-' + 'pe-'  + my_vars['pe_device'] + '-' + date.isoformat(date.today()) + '-' + str(j) + '.set'
         print ('\n 3d. Created PE Audit file is:', pe_service_file)
         with open(pe_service_file,'w') as f4:
              cfg_file = f4.write(cfg_output_pe)  
         f4.close()

         #break 
             

         print(master['agg_template_file'])
         a = 1
         while (a < 6):
             agg = "agg" + str(a)      
             agg_device = "agg" + str(a) + "_device"
             agg_type = "agg" + str(a) + "_device"
             agg_customer_facing_interface  = "agg" + str(a) + "_customer_facing_interface"
             agg_upstream_interface = "agg" + str(a) + "_upstream_interface" 
             print (agg)
             print (agg_device)
             print (agg_type)
             print (agg_customer_facing_interface, agg_upstream_interface) 
             my_vars['agg'] = my_vars[agg]
             my_vars['agg_device'] = my_vars[agg_device]
             my_vars['agg_type'] = my_vars[agg_type]
             my_vars['agg_customer_facing_interface'] = my_vars[agg_customer_facing_interface]
             my_vars['agg_upstream_interface'] = my_vars[agg_upstream_interface]
             print (my_vars['agg_device'],my_vars['agg_type'],my_vars['agg_device'],my_vars['agg_customer_facing_interface'],my_vars['agg_upstream_interface'])
             if (my_vars[agg] == True and my_vars[agg_device] != 'n/a') :
                 my_vars['agg_customer_facing_interface'] = my_vars[agg_customer_facing_interface]
                 my_vars['agg_upstream_interface'] = my_vars[agg_upstream_interface]
                 my_vars['agg_device'] = my_vars[agg_device]
             
             
                 cfg_output_agg = build_jinja2_template(master['agg_template_file'],my_vars)
                 print ('\n 3e. Built the configuration agg based on the Jinja2 template')
                 #device_name = row.pop('device_name')
                 # *******   Output the configuration to a file.   For audit purposes ***** 
                 agg_service_file =  my_vars['service_name'] + '-' + 'agg-' + my_vars['agg_device'] + '-' + date.isoformat(date.today()) + '-' + str(j) + '.cfg'
                 print ('\n 3f. Created agg Audit file is:', agg_service_file)
                 with open(agg_service_file,'w') as f5:
                     cfg_file = f5.write(cfg_output_agg)  
                 f5.close()
             a = a + 1
             


         #exit()
         if ( master['deploy_service'] == True) :
             print ('\n 6. Provision changes on PE')
             print ("Row",my_vars['pe_device'],row['username'])
             ### ******** PUSH the configuration to the PE ****
             try:
                 #    dev = Device(host=my_vars['pe_device'], user=row['username'], password=PASSWORD,mode='telnet',port=23)
                 dev_locked = False
                 #dev = Device(host=my_vars['pe_device'], user=row['username'], password=PASSWORD,port=22)
                 dev = Device(host=my_vars['pe_device'], user='wjohnston', password='Jasper1',port=22)
                 #    print ("host,user,password ",dev['host'],dev['user'],dev['password'])
                 print ("connecting to device ",my_vars['pe_device'])
                 dev.open()
                 #pprint(dev.facts)
                 config = Config(dev)
                 config.lock()
                 dev_locked = True
                 commit_executed = False
                 print("Locked the database")
                 print("pe_service_file=",pe_service_file)
                 print("Load the config file")
                 config.load(path=pe_service_file, merge=True, format="set")
                 #config.rollback(rb_id=1)
                 print ("The changes being made are:")
                 diff = config.pdiff()
                 if (diff == ""):
                     print ("No changes");
                 else:
                     print ("Confirm that the changes can be committed")
                     commit_check = config.commit_check()
                     print (commit_check)
                     print
                     #show system commit to look at commits.
                     print("Committing the changes")
                     commit_executed = "Starting"
                     config.commit(comment=pe_service_file )
                     print("Changes committed")
                     commit_executed = True
                     #print (commit_detail)
                     #print (etree.tostring(commit_detail, encoding='unicode'))


             except CommitError as err:
                        print ("The Config has errors and could not be committed" ,err)
                        #print (repr(err))
             except LockError as err:
                 print ("The Config databased was locked! ",err)
             except ConnectTimeoutError as err:
                 print ("Connection Timeout from ", my_vars['pe_device'],err)
             #except _raiseParseError as err:
             #    print ("Could not print output of commit ")
             except RuntimeWarning as err:
                 print ("Runtime error",err)
             except:
                 print ("Unexpected Error - contact NETENG", sys.exc_info()[0])

             #commit_executed will show a state of "Starting" if a commit was attempted but failed.
             #This means rollback 0    
             if (commit_executed == "Starting") :
                 config.rollback(rb_id=0)

             #if exception was raised or not
             if dev_locked == True: 
                 print("Unlocking the config file database")
                 config.unlock()
                 print ("Closing the connection to the device")
                 dev.close()
                 
             print ('\n 5. Provision changes on MRV')
             
             establish_netmiko_conn(device_name, row, mrv_service_file,my_vars['service_name'])

                 
              
             print ('\n 7. Provision changes on aggswitches')
#                  section to completed in the future.   Very similar to PE.

         if ( master['test_service'] == True) :
             print ('\n 10. Test Service End to End')

#show status of "VPLS"
             #try:
             with Device(host=my_vars['pe_device'], user='wjohnston', password='Jasper1',port=22) as dev:
                 if (my_vars['service_product'] == 'e-lan'):
                     data = dev.rpc.get_vpls_connection_information({'format':'text'},instance=my_vars['service_name'])
                     cmd = 'show vpls connections instance ' + my_vars['service_name']
                     print(dev.cli(cmd))
                 else:
                     data = dev.rpc.get_l2vpn_connection_information(instance=my_vars['service_name'])
                     cmd = 'show l2vpn connections instance ' + my_vars['service_name']
                     print(dev.cli(cmd))
                 #dictdata = xmltodict.parse(data)
                 #pprint(dictdata)
                 #print (data)
                 #data = dev.cli('show vpls connections ')
                 #data = dev.cli('netconf \n <rpc> \n <get-vpls-connection-information format="text"> \n <instance>EVP-LAN3</instance> \n </get-vpls-connection-information> \n </rpc> \n </rpc>')
                 #print ('data',data)
                 #parse = CiscoConfParse(data)
                 #objs = parse.find_objects("^Instance ")
                 #print (objs)
                 #pprint (etree.tostring(data, encoding='unicode'))
                 #    dev = Device(host=my_vars['pe_device'], user=row['username'], password=PASSWORD,mode='telnet',port=23)
                 #dev_locked = False
                 #dev = Device(host=my_vars['pe_device'], user=row['username'], password=PASSWORD,port=22)
                 #dev = Device(host=my_vars['pe_device'], user='wjohnston', password='Jasper1',port=22)
                 #    print ("host,user,password ",dev['host'],dev['user'],dev['password'])
                 #print ("connecting to device ",my_vars['pe_device'])
                 #dev.open()
                 #pprint(dev.facts)
                 #print (dev.display_xml_rpc('show vpls connections instance '))
                 #data = dev.rpc.get-vpls-connection-information(normalize=True)
                 #data = dev.rpc.get-interface-information()
                 #cmd = 'show vpls connections instance ' + my_vars['service_name']
                 #print(dev.cli(cmd))
                 #dev.close()
                 #print(data)
                 #pe1 = {
                 #    'device_type': 'juniper',
                 #    'ip':'10.92.6.61',
                 #    'username': 'wjohnston',
                 #    'password': 'Jasper1',
                 #    'port': 22,
                 #}
                 #pe1_rtr = ConnectHandler(**pe1)
                 #outp = pe1_rtr.send_command('netconf \n <rpc> \n <get-vpls-connection-information format="text"> \n <instance>EVP-LAN3</instance> \n </get-vpls-connection-information> \n </rpc> \n </rpc>')
                 #print ('data',outp)
                 #dir(pe1_rtr)
                 #print (etree.tostring(data, encoding='unicode'))
             #except ConnectTimeoutError as err:
             #    print ("Connection Timeout from ", my_vars['pe_device'],err)
             #except _raiseParseError as err:
             #    print ("Could not print output of commit ")
             #except RuntimeWarning as err:
             #    print ("Runtime error",err)
             #except:
             #    print ("Unexpected Error - contact NETENG", sys.exc_info()[0])

             test_ip = '1.1.1.1'
             if ( my_vars['service_ip']) :
                 if j == 1:
                    test_ip = (my_vars['service_ip'].split(".")[0] + "." + my_vars['service_ip'].split(".")[1] + "." + my_vars['service_ip'].split(".")[2] + "." + "2")
                 else:
                    test_ip = (my_vars['service_ip'].split(".")[0] + "." + my_vars['service_ip'].split(".")[1] + "." + my_vars['service_ip'].split(".")[2] + "." + "1")
                                                                                                                        
             test_service(device_name, row, mrv_service_file,my_vars['service_name'],my_vars, test_ip)

             

         
         #print (j,"end for")
         j += 1
         #            break
f2.close()
#print(read_csv)



#if __name__ == "__main__":
#    main()
