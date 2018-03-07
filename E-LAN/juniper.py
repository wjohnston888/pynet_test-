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
#from jnpr.junos.device import Device
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
from jnpr.junos.rpcmeta import _RpcMetaExec
import jxmlease
from ciscoconfparse import CiscoConfParse
import os, errno
import time
import socket


reload (sys)
sys.setdefaultencoding('utf8')

PASSWORD = getpass()


dev = Device(host='10.92.6.61', user='wjohnston', password='Jasper1',port=22)
dev.open()
rsp = dev.rpc.get_vpls_connection_information(instance=my_vars['service_name'])
pprint (etree.tostring(rsp, encoding='unicode'))
dev.close()

 #show status of "VPLS"
 #try:
#with Device(host='10.92.6.61', user='wjohnston', password='Jasper1',port=22) as dev:
     #data = dev.rpc.get-vpls-connection-information(instance='EVP-LAN3')
#    data = dev.rpc.get_interface-information()
    #data = dev.rpc.get-l2vpn-connection-information()
    #data = dev.rpc.get-vpls-connection-information()
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
     #print (dev.display_xml_rpc('show vpls connections'))
     #data = dev.rpc.get-vpls-connection-information(normalize=True)
     #data = dev.rpc.get-interface-information()
     #print(dev.cli('show vpls connections | display xml'))
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

         
         #print (j,"end for")
         #j += 1
         #            break
#f2.close()
#print(read_csv)



#if __name__ == "__main__":
#    main()
