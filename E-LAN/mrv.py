#!/usr/bin/env/python
'''
This is a script can check, render, configure, and test a MEF service on
     MRV Vseries devices, Juniper PEs, and Juniper EX agg switches.
1.  First read key service variables from service_files.yml in a master dictionary
2.  Read each service file in either YML or RTF format.   mrv_service(n).RTF|YML
3.  Build the Configlets for all devices and store it in the Service Activation Folder define in master dictionary
4.  Deploy Services if requested master dictionary
5.  Test Services if requested in master dictionary
2.  The Configuration change is saved and then pushed to the device.
INPUT FILES
   mrv_files.yml
   service_vars_n.(rtf|yml) - defined in master dictionary
OUTPUT FILES
   mrv_service_SERVICE-NAME-Date.(cfg|set)
'''
# pylint: disable=C0303, C0301
from __future__ import print_function
from __future__ import unicode_literals

from getpass import getpass

import sys
from datetime import date
import os
import time
from socket import gethostbyaddr
from socket import gethostbyname
from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
from lxml import etree
from jinja2 import Environment, BaseLoader
from jnpr.junos.device import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import CommitError, ConfigLoadError, ConnectAuthError, ConnectClosedError, ConnectNotMasterError, ConnectRefusedError, LockError
from jnpr.junos.exception import PermissionError, ConnectError, ConnectTimeoutError, SwRollbackError, UnlockError, ConnectUnknownHostError
import re

from ciscoconfparse import CiscoConfParse
import yaml



reload(sys)
#sys.setdefaultencoding('utf8')

print ("MRV Account admin")
#PASSWORD = getpass()
PASSWORD = 'mrv001'
iuser = raw_input("Juniper Username: ")
print (iuser)
PASSWORD2 = getpass()
PASSWORD2 = PASSWORD2.strip()



def nslookitup(ip):
    ''' Lookup and IP address and return the fqdn of the device'''
    try:
        output = gethostbyaddr(ip)
        return output[0]
    except:
        output = "not found"
        return output


def pre_check_edge_device(my_vars, username, PASSWORD, DEBUG):
    '''Validate some on the Edge device'''
    if DEBUG:
        print("Stubs to be filled in")
        print("Check if mostly already configured")
        print("Check VLANS")
        print("Check IPs")
        print("Check Port Description")
    try:
        print('-' * 40)
        print("Establish SSH Conn: {}".format(my_vars['edge_device']))
        netmiko_dict = {}
        if 'edge_ip' in my_vars.keys():
            netmiko_dict['host'] = my_vars['edge_ip']
        else:
            netmiko_dict['host'] = nslookitup(netmiko_dict['device'])
            if DEBUG:
                print ("IP resolved as ", netmiko_dict['host'])
        netmiko_dict['device_type'] = my_vars['edge_device_type']
        netmiko_dict['username'] = username
        netmiko_dict['password'] = PASSWORD

        #connect to MRV device
        net_connect = ConnectHandler(**netmiko_dict)
        time.sleep(2)  #MRVs take a long time to login.   Take a short nap.
        try:
            net_connect.enable()  #aquire enable mode
            print(net_connect.find_prompt())
            print ('\n 1.5a Go get the current config for ', my_vars['edge_device'])
            show_cmd = "show run"
            show_test = net_connect.send_command(show_cmd)
            net_connect.disconnect()
        except:
            print('could not get into enable mode, config test')


        with open('m.cfg', 'w') as fm:
            fm.write(show_test)
        fm.close()

    except NetMikoAuthenticationException:
        print("SSH login failed")

    vifexists = False
    pdescrip = False
    action_list = False
    access_list = False
    
    mrv_cfg = CiscoConfParse('m.cfg')
    interface_objs = mrv_cfg.find_objects("interface vlan")
    for obj in interface_objs:
        interface_name = obj.text
        #print (interface)
        if interface_name.find(str(my_vars['s_vlan'])) != -1:
            print("Service VLAN already defined: ", interface_name)
        else:
            vifexists = True

    port_objs = mrv_cfg.find_objects("port description")
    for obj in port_objs:
        port_description = obj.text
        #print (interface)
        if port_description.find('port description '+str(my_vars['c_ports'])+' ') != -1:
            print("Customer Port is already defined: ", port_description)
        else:
            pdescrip = True

    action_objs = mrv_cfg.find_objects("action-list reglr_ing_"+my_vars['service_name'])
    for obj in action_objs:
        action_description = obj.text
        #print (interface)
        if action_description.find("action-list reglr_ing_"+my_vars['service_name']) != -1:
            print("Action list is already defined: ", action_description)
        else:
            action_list = True


    access_objs = mrv_cfg.find_objects("port access-group")
    for obj in access_objs:
        access_description = obj.text
        #print (interface)
        if (access_description.find("port access-group ingress_acl_port-"+str(my_vars['c_ports'])) != -1) or (access_description.find("port access-group egress_acl_port-"+str(my_vars['c_ports'])) != -1):
            print("Access list is already defined: ", access_description)
        else:
            access_list = True

    if vifexists or pdescrip or action_list or access_list:
        print ("Service already partly defined")
        return False
    else: 
        return True


def pre_check_pe_device(my_vars, username, PASSWORD, DEBUG):
    ''' validate design parameters on on the PE'''
    if DEBUG:
        print("Stubs to be filled in")
        print("Check if mostly already configured")
        print("Check route target ")
        print('Check route distinquisher')
        print("Site ID")
        print("RT,RD")
        print("Check Port")
        print("Check VLANS")
        print("Check Port Description")
    print("Checking RT and RD")
    

    #commit_executed will show a state of "Starting" if a commit was attem
    # Check RT by going after the Route Reflector and seeing if Route Target is defined
    try:
        with Device(host='clgrab42mmrrf001', user=username, password=PASSWORD, port=22) as rr_dev:
    
            route_target_rr_data = rr_dev.rpc.get_route_information({'format':'text'}, 
                                                                    table='bgp.rtarget')
            route_target_rr_test = etree.tostring(route_target_rr_data)
            #route_l2vpn_rr_data = rr_dev.rpc.get_route_information({'format':'text'}, 
            #                                                       table='bgp.l2vpn.0')
            #route_l2vpn_rr_test = etree.tostring(route_l2vpn_rr_data)
    
            with Device(host=my_vars['pe_device'], user=username, password=PASSWORD, port=22) as dev:
                route_target_pe_cmd = 'show configuration routing-instances ' + my_vars['service_name']
                route_target_pe_test = (dev.cli(route_target_pe_cmd))
                route_distinquisher_pe_cmd = 'show configuration routing-instances '
                route_distinquisher_pe_test = (dev.cli(route_distinquisher_pe_cmd))
    
                print("Checks for device Route target against the route reflector", 'clgrab42mmrrf001')
                if DEBUG:
                    print (route_target_rr_test)
                    route_target_rr_cmd = 'show route table bgp.target '
                    print (dev.cli(route_target_rr_cmd))
                if route_target_rr_test.find('64512:'+my_vars['L2VPLS_RT']) != -1:
                    print('#' * 60)
                    print('Route Target, ', my_vars['L2VPLS_RT'], ' Is in use according to Route Reflector ', 
                          'CLGRAB42MMRRF001')
                else:
                    print('#' * 60)
                    print('Route Target, ', my_vars['L2VPLS_RT'], ' Is not in use according to Route Reflector ', 
                          'CLGRAB42MMRRF001')
                    print('#' * 60)
    
                try:
                    lo_ip_pe = gethostbyname(my_vars['pe_device'])
                except:
                    print("Could not get the loopback IP")
                    return False
                
                RD = lo_ip_pe + ":" + my_vars['L2VPLS_RT'].split(':')[1]
                RT = "64512:" + my_vars['L2VPLS_RT'].split(':')[1]
                print('LO IP of PE (', my_vars['pe_device'], ') is ', lo_ip_pe)
                print('RD = ', RD)
                print('RT = ', RT)
                
                if route_target_pe_test.find('vrf-target target:'+RT) != -1:
                    print('Route Target, ', RT, ' Is in use already for this VPN, so all is good')
                else:
                    print('Route Target, ', RT, ' Has not been used for this VPN')
                    
                if route_distinquisher_pe_test.find(RD) != -1:
                    print('Route Target, ', RD, ' Is in use already for this VPN, so all is good')         
                return True
            
        with Device(host=my_vars['pe_device'], user=username, password=PASSWORD, port=22) as dev:
            pe_interface = my_vars['pe_customer_facing_interface']+"."+str(my_vars['s_vlan'])
            interface_data = dev.rpc.get_interface_information({'format':'text'}, interface_name=pe_interface)
            interface_test = etree.tostring(interface_data)
            print("Checks for device", my_vars['pe_device'])    
            if DEBUG:
                print (interface_test)
                cmd = 'show interface ' + my_vars['pe_customer_facing_interface']+"."+str(my_vars['s_vlan'])  
                print (dev.cli(cmd))   
            if interface_test.find(my_vars['pe_customer_facing_interface']+"."+str(my_vars['s_vlan'])) != -1:
                print('#' * 60)
                print('VLAN ', my_vars['s_vlan'], 'is already defined on the customer facing Interface')
                if interface_test.find(my_vars['customer_number']+":"+str(my_vars['service_name'])) != -1:
                    print("VLAN ", my_vars['s_vlan'], " is defined for this service so all is good")
                else:
                    print("VLAN appears to be defined for another service")
                print('#' * 60)
                
            else:
                print('#' * 60)
                print('VLAN is not in use on the customer facing Interface.')
                print('#' * 60)
        
        with Device(host=my_vars['pe_device'], user=username, password=PASSWORD, port=22) as dev:
            if my_vars['service_product'] == 'e-lan':
                vpls_data = dev.rpc.get_vpls_connection_information({'format':'xml'}, instance=my_vars['service_name'])
                #parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
                vpls_test = etree.tostring(vpls_data)
                print(vpls_data)                
                if DEBUG:
                    print (vpls_test)
                    cmd = 'show vpls connections instance ' + my_vars['service_name']   
                    print (dev.cli(cmd))   
                if vpls_test.find(" rmt   Up ") != -1:
                    print('#' * 60)
                    print('VPLS connection confirmed for atleast one site')
                    print('#' * 60)
                else:
                    print('#' * 60)
                    print('Test does not have any other sites up, if this is the first site, all is good.')
                    print('#' * 60)
            else:
                data = dev.rpc.get_l2vpn_connection_information(instance=my_vars['service_name'])
                l2vpn_test = etree.tostring(data)
                if DEBUG:
                    print (l2vpn_test)  
                    cmd = 'show l2vpn connections instance ' + my_vars['service_name']
                    l2vpn_test = dev.cli(cmd)    
                if l2vpn_test.find(" rmt   Up ") != -1:
                    print('#' * 60)
                    print('Test Successful, L2VPN connection confirmed to be operational')
                    print('#' * 60)
                else:
                    print('#' * 60)
                    print('The other site does not appear to be connected, if this is the first site, all is good.')
                    print('#' * 60)
                    
    except ConnectClosedError as err:
        print ("Connect Closed Error", err)
    except ConnectUnknownHostError as err:
        print ("Tried to connecte to unkown host", err)
    except ConnectNotMasterError as err:
        print ("Not Connected to the master", err)
    except PermissionError as err:
        print ("Permissions Error", err)
    except ConfigLoadError as err:
        print ("Cannot Load the Config", err)
    except ConnectError as err:
        print ("Cannot Connect to the device", err)
    except ConnectAuthError as err:
        print ("Cannot Connect authenticate to the device", err)
    except ConnectRefusedError as err:
        print ("Connection Refused", err)
    
    except ConnectTimeoutError as err:
        print ("Connection Timeout from ", my_vars['pe_device'], err)
    #except _raiseParseError as err:
    #    print ("Could not print output of commit ")
    except:
        print ("Unexpected Error - contact NETENG", sys.exc_info()[0])
        
        
def pre_check_agg_device(my_vars, username, PASSWORD, DEBUG):
    ''' Pre-check some agg device parameters '''
    if DEBUG:
        print("Stubs to be filled in")
        print("Check if mostly already configured")
        print("Check port")
        print("Check VLANS")
        print("Check Port Description")
        print(my_vars, username, PASSWORD, DEBUG)
 

def copy_service_vars(j, master, my_vars, DEBUG):
    ''' Purpose of this procedure is to create a copy of the service input file so it can be compared against output '''
    global yaml_str
    my_vars['date'] = date.isoformat(date.today())
    
    
    yaml_service_file = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + "mrv_service_file_" + "_ "+ date.isoformat(date.today()) + ".yml"
    #output_file = my_vars['service_name'] + '-birth-'  + date.isoformat(date.today()) + '.txt'
    #err_file = my_vars['service_name'] + '-birth-'  + date.isoformat(date.today()) + '.err'
    if DEBUG:
        print ('\n copy YML file is:', yaml_service_file)
    yaml_file_path1 = master['file_path'] + my_vars['customer_number'] + "/" 
    yaml_file_path2 = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + "mrv_service_file_" + str(j) + "_ "+ date.isoformat(date.today()) +".yml"
    #output_file_path = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + output_file
    #err_file_path = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + err_file
    service_vars_file_txt = master['service_vars'].split('.')[0] + str(j) +'.' + 'txt'
    service_vars_file_yml = master['service_vars'].split('.')[0] + str(j) +'.' + 'yml'
    directory1 = os.path.dirname(yaml_file_path1)
    directory2 = os.path.dirname(yaml_file_path2)
    try:
        os.stat(directory1)
        try:
            os.stat(directory2)
        except:
            os.mkdir(directory2)
    except:
        os.mkdir(directory1)
        try:
            os.stat(directory2)
        except:
            os.mkdir(directory2)
            
    #print (service_vars_file)
    
    #sys.stderr.write(output_file_path)
    #sys.stdout = open(output_file_path,'w+')
    #sys.stderr = open(err_file_path,'w+')
    
    yaml_str = ""
    #copy the Service Variable file to the audit directory
    try:
        os.stat(service_vars_file_yml)
        with open(service_vars_file_txt) as yml1:
            yaml_str = yaml_str + yml1.read()
            yml1.close()   
    except:
        try:
            os.stat(service_vars_file_txt)
            with open(service_vars_file_txt) as yml1:
                yaml_str = yaml_str + yml1.read()
            yml1.close()  
        except:
            print ("Hand a problem reading the service file")  
    
    with open(yaml_file_path2, 'w') as yml3:
        yml3.write(yaml_str)
    yml3.close()
    # the way to do it via a dictionary
    #print (yaml_str)
    #data = YAML.load(yaml_str, Loader=YAML.RoundTripLoader)
    #    YAML.dump(data, yml3, Dumper=YAML.RoundTripDumper)
        
    yaml_file_path2 = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + "mrv_service_file_" + str(j) + "_ "+ date.isoformat(date.today()) +".yml"
        
    print("\nCOPIED YML ", yaml_file_path2, my_vars['customer_name'], my_vars['customer_number'], ':', my_vars['service_name'], my_vars['service_product'], 'Version', my_vars['service_version'], 'Service Type', my_vars['service_type'], 'template version', my_vars['template_version'])
    
        
def render_agg_devices(j, master, my_vars, DEBUG):
    ''' Render the aggregation device configuration '''
    if 'service_version' not in my_vars.keys():
        my_vars['service_version'] = '2.0'  
    if 'template_version' not in my_vars.keys():
        my_vars['template_version'] = '1.0'
    agg_EX_template_file = master['agg_EX_template_file'] + "_" + my_vars['service_product'] + ".j2"
    
    #print(agg_EX_template_file)
    if DEBUG:
        print(agg_EX_template_file)
    a = 1
    while a < 6:
        agg = "agg" + str(a)
        agg_device = "agg" + str(a) + "_device"
        agg_type = "agg" + str(a) + "_device"
        agg_customer_facing_interface = "agg" + str(a) + "_customer_facing_interface"
        agg_upstream_interface = "agg" + str(a) + "_upstream_interface"
        if DEBUG:
            print (agg)
            print (agg_device)
            print (agg_type)
            print (agg_customer_facing_interface, agg_upstream_interface)
        my_vars['agg'] = my_vars[agg]
        my_vars['agg_device'] = my_vars[agg_device]
        my_vars['agg_type'] = my_vars[agg_type]
        my_vars['agg_customer_facing_interface'] = my_vars[agg_customer_facing_interface]
        my_vars['agg_upstream_interface'] = my_vars[agg_upstream_interface]
        if DEBUG:
            print (my_vars['agg_device'], my_vars['agg_type'], my_vars['agg_device'], my_vars['agg_customer_facing_interface'], my_vars['agg_upstream_interface'])
    
        if my_vars[agg] is True and my_vars[agg_device] != 'n/a':
            #print ("Rendered Config for ", my_vars['agg_device'], my_vars['agg_type'], my_vars['agg_device'], my_vars['agg_customer_facing_interface'], my_vars['agg_upstream_interface'])
            my_vars['agg_customer_facing_interface'] = my_vars[agg_customer_facing_interface]
            my_vars['agg_upstream_interface'] = my_vars[agg_upstream_interface]
            my_vars['agg_device'] = my_vars[agg_device]
            #build configlet 
            cfg_output_agg = build_jinja2_template(master['template_path'] + agg_EX_template_file, my_vars, DEBUG)
            
            #device_name = row.pop('device_name')
            # *******   Output the configuration to a file.   For audit purposes *****
            agg_service_file = my_vars['service_name'] + '-' + 'agg-' + my_vars['agg_device'] + '-' + date.isoformat(date.today()) + '-' + str(j) + '.set'
            if DEBUG:
                print ('\n  Created agg Audit file is:', agg_service_file)
            agg_file_path = master['file_path'] + my_vars['customer_number'] + "/"  +my_vars['service_name'] + "/" + agg_service_file
            
            with open(agg_file_path, 'w') as f5:
                cfg_file = f5.write(cfg_output_agg)
            f5.close()
            if DEBUG:
                print (cfg_file)
            print("RENDERED AGG", my_vars['customer_name'], my_vars['customer_number'], ':', my_vars['service_name'], my_vars['service_product'], 'Version', my_vars['service_version'], 'Service Type', my_vars['service_type'], 'template version', my_vars['template_version'])
            
        a = a + 1
        
    
def render_pe_device(j, master, my_vars, DEBUG):
    ''' Render the Configuration on the PE '''
    my_vars['date'] = date.isoformat(date.today())
    if DEBUG:
        print(master['pe_template_file'])
    if 'service_version' not in my_vars.keys():
        my_vars['service_version'] = '2.0'  
    if 'template_version' not in my_vars.keys():
        my_vars['template_version'] = '1.0' 
    
    # Build the Configlet
    cfg_output_pe = build_jinja2_template(master['template_path'] + pe_template_file, my_vars, DEBUG)
    pe_service_file = my_vars['service_name'] + '-' + 'pe-'  + my_vars['pe_device'] + '-' + date.isoformat(date.today()) + '-' + str(j) + '.set'
    pe_file_path = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + pe_service_file
    
    with open(pe_file_path, 'w') as f4:
        f4.write(cfg_output_pe)
    f4.close()
    print("RENDERED PE", my_vars['customer_name'], my_vars['customer_number'], ':', my_vars['service_name'], my_vars['service_product'], 'Version', my_vars['service_version'], 'Service Type', my_vars['service_type'], 'template version', my_vars['template_version'])
        
        
def render_edge_device(j, master, my_vars, DEBUG):
    #DEBUG = True
    my_vars['date'] = date.isoformat(date.today())
    if 'service_version' not in my_vars.keys():
        my_vars['service_version'] = '2.0'  
    if 'template_version' not in my_vars.keys():
        my_vars['template_version'] = '1.0'#device_name = row.pop('device_name')
    my_vars['date'] = date.isoformat(date.today())
    my_vars['oam_ma'] = my_vars['L2VPLS_RT'].split(":")[1]
    my_vars['mrv_device'] = device_name
    #print("calling cfg=output = build_jinja2_template", master['pe_template_file'], my_vars, DEBUG)
    # Build Edge Device Configlet
    cfg_output = build_jinja2_template(master['template_path'] + mrv_template_file, my_vars, DEBUG)
    # *******   Output the configuration to a file.   For audit purposes *****
    mrv_service_file = my_vars['service_name'] + '-mrv-' + device_name + '-' + date.isoformat(date.today()) + '-' + str(j) + '.cfg'
    #output_file = my_vars['service_name'] + '-birth-'  + date.isoformat(date.today()) + '.txt'
    #err_file = my_vars['service_name'] + '-birth-'  + date.isoformat(date.today()) + '.err'
    if DEBUG:
        print ('\n 4b. Created MRV Audit file is:', mrv_service_file)
    mrv_file_path1 = master['file_path'] + my_vars['customer_number'] + "/" 
    mrv_file_path2 = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + mrv_service_file
    #output_file_path = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + output_file
    #err_file_path = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + err_file
    directory1 = os.path.dirname(mrv_file_path1)
    directory2 = os.path.dirname(mrv_file_path2)
    try:
        os.stat(directory1)
        try:
            os.stat(directory2)
        except:
            os.mkdir(directory2)
    except:
        os.mkdir(directory1)
        try:
            os.stat(directory2)
        except:
            os.mkdir(directory2)
                
    with open(mrv_file_path2, 'w') as f3:
        f3.write(cfg_output)
    f3.close()
    print("\nRENDERED EDGE ", my_vars['customer_name'], my_vars['customer_number'], ':', my_vars['service_name'], my_vars['service_product'], 'Version', my_vars['service_version'], 'Service Type', my_vars['service_type'], 'template version', my_vars['template_version'])
    
    
def upload_edge_device_configuration(j, my_vars, config_file, username, PASSWORD, DEBUG):
    '''Establish Netmiko SSH connection; upload config file.'''
    #DEBUG = True
    if DEBUG:
        print (j,my_vars,config_file,username,DEBUG)
    try:
        print ("Upload Edge Device Config", '-' * 40)
        print ("Establish SSH Conn: {}".format(device_name))
        netmiko_dict = {}
        if 'edge_ip' in my_vars.keys():
            netmiko_dict['host'] = my_vars['edge_ip']
        else:
            netmiko_dict['host'] = nslookitup(netmiko_dict['device'])
            if DEBUG:
                print ("IP resolved as ", netmiko_dict['host'])
        netmiko_dict['username'] = username
        netmiko_dict['password'] = PASSWORD
        netmiko_dict['device_type'] = my_vars['edge_device_type']
        net_connect = ConnectHandler(**netmiko_dict)   #connect to MRV device
        print ("uploading ", config_file, "to ", netmiko_dict['host'])
        time.sleep(2)  #MRVs take a long time to login.   Take a short nap.
        try:
            print('Attempting enable mode')
            net_connect.enable()
            print(net_connect.find_prompt())
            try:
                print('Attempting config mode')
                print(net_connect.config_mode())
                try:
                    print('Attempting to upload config changes')
                    print(net_connect.send_config_from_file(config_file)) 
                    print ("uploaded ", config_file, "to ", netmiko_dict['host'])
                except:
                    print ("Could not upload config file, ", config_file)
            except:
                print ("Could not get enable mode")
        except:
            print('could not get into enable mode, config not loaded')
    except NetMikoAuthenticationException:
        print("SSH login failed")
       
       
def upload_pe_device_configuration(j, master, my_vars, username, PASSWORD, DEBUG):
    ''' Upload PE Configlet to PE '''

    ### ******** PUSH the configuration to the PE ****
    commit_executed = False
    my_vars['date'] = date.isoformat(date.today())
    pe_service_file = my_vars['service_name'] + '-' + 'pe-'  + my_vars['pe_device'] + '-' + date.isoformat(date.today()) + '-' + str(j) + '.set'
    #pe_file_path = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + pe_service_file
    try:
        COMMIT_SUCCESSFUL = False
        NO_CHANGE = True
        dev_locked = False
        #dev = Device(host=my_vars['pe_device'], user=row['username'], password=PASSWORD2, port=22)
        dev = Device(host=my_vars['pe_device'], user=username, password=PASSWORD, port=22)
        #    print ("host,user,password ",dev['host'],dev['user'],dev['password'])
        print ("connecting to device ", my_vars['pe_device'])
        dev.open()
        #pprint(dev.facts)
        config = Config(dev)
        config.lock()
        dev_locked = True
        if DEBUG:
            print("Locked the database")
        print("pe_service_file=", pe_service_file)
        pe_file_path2 = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + pe_service_file
        print("Load the config file")
        print("pe_file_path2=", pe_file_path2)
        config.load(path=pe_file_path2, merge=True, format="set")

        #config.rollback(rb_id=1)
        print ("The changes being made are:")
        diff = config.pdiff()
        if diff is None:
            print ("No changes")
            NO_CHANGE = True
        else:
            print ("Confirm that the changes can be committed")
            commit_check = config.commit_check()
            print (commit_check)
            #show system commit to look at commits.
            print("Committing the changes")
            commit_executed = "Starting"
            config.commit(comment=pe_service_file)
            print("Changes committed")
            COMMIT_SUCCESSFUL = True
            commit_executed = True
            #print (commit_detail)
            #print (etree.tostring(commit_detail, encoding='unicode'))


    except ConnectClosedError as err:
        print ("Connect Closed Error", err)
    except ConfigLoadError as err:
        print ("Cannot Load the Config", err)
    except ConnectUnknownHostError as err:
        print ("Tried to connecte to unkown host", err)
    except ConnectNotMasterError as err:
        print ("Not Connected to the master", err)
    except SwRollbackError as err:
        print ("Could not Rollback", err)
    except PermissionError as err:
        print ("Permissions Error", err)
    except ConfigLoadError as err:
        print ("Cannot Load the Config", err)
    except ConnectError as err:
        print ("Cannot Connect to the device", err)
    except ConnectAuthError as err:
        print ("Cannot Connect authenticate to the device", err)
    except ConnectRefusedError as err:
        print ("Connection Refused", err)
    except CommitError as err:
        print ("The Config has errors and could not be committed", err)
        #print (repr(err))
    except LockError as err:
        print ("The Config database was locked! ", err)
    except ConnectTimeoutError as err:
        print ("Connection Timeout from ", my_vars['pe_device'], err)
    #except _raiseParseError as err:
    #    print ("Could not print output of commit ")
    except RuntimeWarning as err:
        print ("Runtime error", err)
    except:
        print ("Unexpected Error - contact NETENG", sys.exc_info()[0])
    #commit_executed will show a state of "Starting" if a commit was attempted but failed.
    #This means rollback 0
    if commit_executed == "Starting":
        config.rollback(rb_id=0)

#
    #if exception was raised or not
    if dev_locked is True:
        print("Unlocking the config file database")
        try:
            config.unlock()
        except UnlockError as err:
            print ("Could not unlock the config.   Please contact NetEng ",err)

        print ("Closing the connection to the device")
        try:
            dev.close()
        except:
            print ("Could not close the device.   Please contact NetEng ",err)
            
        
    bool(COMMIT_SUCCESSFUL or NO_CHANGE)

                   
def test_pe_device_service(my_vars, username, PASSWORD, DEBUG):  
    ''' Perform various tests on the PE to confirm service is working 
        Most tests will fail until atleast two points are added '''
     
    if DEBUG:
        print ("show status of VPLS for ELAN and L2VPN for all others")
        print ("logging in " + iuser + "#"+"#")
    try:
        with Device(host=my_vars['pe_device'], user=username, password=PASSWORD, port=22) as dev:
            if my_vars['service_product'] == 'e-lan':
                data = dev.rpc.get_vpls_connection_information({'format':'text'}, instance=my_vars['service_name'])
                #parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
                vpls_test = etree.tostring(data)
                    
                if DEBUG:
                    print (vpls_test)
                    cmd = 'show vpls connections instance ' + my_vars['service_name']   
                    print (dev.cli(cmd))   
                if vpls_test.find(" rmt   Up ") != -1:
                    print('#' * 60)
                    print('Test Successful, VPLS connection confirmed for atleast one site')
                    print('#' * 60)
                else:
                    print('#' * 60)
                    print('Test does not have any other sites up, if this is the first site, all is good.')
                    print('#' * 60)
            else:
                data = dev.rpc.get_l2vpn_connection_information(instance=my_vars['service_name'])
                l2vpn_test = etree.tostring(data)
                if DEBUG:
                    print (l2vpn_test)  
                    cmd = 'show l2vpn connections instance ' + my_vars['service_name']
                    l2vpn_test = dev.cli(cmd)    
                if l2vpn_test.find(" rmt   Up ") != -1:
                    print('#' * 60)
                    print('Test Successful, L2VPN connection confirmed to be operational')
                    print('#' * 60)
                else:
                    print('#' * 60)
                    print('The other site does not appear to be connected, if this is the first site, all is good.')
                    print('#' * 60)
    except:
        print ("Error: Could not connect to PE, please check device name, username, and password")


def test_edge_device_service(my_vars, test_ip, username, PASSWORD, DEBUG):
    ''' Perform various tests on the edge Device to confirm service is working
        Most tests will fail until atleast two points are added '''
    try:
        print('-' * 40)
        print("Establish SSH Conn: {}".format(my_vars['edge_device']))
        netmiko_dict = {}
        if 'edge_ip' in my_vars.keys():
            netmiko_dict['host'] = my_vars['edge_ip']
        else:
            netmiko_dict['host'] = nslookitup(netmiko_dict['device'])
            if DEBUG:
                print ("IP resolved as ", netmiko_dict['host'])
        netmiko_dict['device_type'] = my_vars['edge_device_type']
        netmiko_dict['username'] = username
        netmiko_dict['password'] = PASSWORD
        
        if DEBUG:
            print ("NETMIKO...", netmiko_dict, "...NETMIKO")
        #connect to MRV device
        net_connect = ConnectHandler(**netmiko_dict)
        time.sleep(2)  #MRVs take a long time to login.   Take a short nap.
        try:
            net_connect.enable()  #aquire enable mode
            #print(net_connect.find_prompt())
            #print('\n 5.3. Verifying configuration and Service \n')
                      
            print ('\n Verifying that the remote MEPs are reachable')
            rmep_cmd = "show ethernet oam domain 2 " + " service " + str(my_vars['oam_ma']) + " mep " + str(my_vars['c_ports']) + str(my_vars['site_id'])+ " rmeps"
            rmep_test = net_connect.send_command(rmep_cmd)
            #print (rmep_cmd)
            #print (rmep_test)
            if rmep_test.find(" Up ") != -1:
                print ('#' * 60)
                print ('Test Successful, Service domain RMEPS links are established ')
                print ('MAC address is up')
                print ("#" * 60)
            elif rmep_test.find(" Dn ") != -1:
                print ("#'" * 60)
                print ("Test NOT Successful, Service OAM link NOT established")
                print ("This may mean link between ENNI and NNI are in place but customer interface is down")
                print ("#" * 60)
            else:
                print ("Error ccm status not known")
            if DEBUG:
                print(rmep_test)           
                      
            #print ('Verifying that the SOAM link is up')
            #print('Verifying CCM status')
            ccm_test = net_connect.send_command("show ethernet oam ccm\n")
            if DEBUG:
                print(ccm_test)
            if ccm_test.find(" Up ") != -1:
                print('#' * 60)
                print('Test Successful, Service OAM link established, Customer UNIs are inplace')
                print('MAC address is up')
                print('#' * 60)
            elif ccm_test.find(" Dn ") != -1:
                print('#' * 60)
                print('Test NOT Successful, Service OAM link NOT established')
                print("This may mean link between two SuperNet endpoints are in place but customer interface is down")
                print('#' * 60)
            else:
                print ("Error ccm status not known")           

            if test_ip <> "355.1.1.1":
                mos_command = 'ping ' + test_ip
                ping_response = net_connect.send_command(mos_command)
                print ("Verifying ICMP connectivity")
                if DEBUG:
                    print("\n", ping_response)
                if ping_response.find('bytes from') != -1:
                    print ('#' * 60)
                    print ("Successful Ping, Connectivity is in place")
                    print ('#' * 60)
                else:
                    print ("Not Connected yet")
                print("\n")
        except:
            print('could not get into enable mode, config test')
    except NetMikoAuthenticationException:
        print("SSH login failed")


def calc_cbs(bandwidth, mtu=2004):
    '''    Calculate the CBS based on the bandwidth supplied '''
    bursttime = .005# 5ms
    cbs = bursttime * bandwidth * 1000000 /8
    if (cbs < mtu*8 and cbs != 0): # ensure CBS is atleast 8 times the MTU
        cbs = mtu*8
    #print(cbs)
    return int(cbs)


def get_all_cbs_values(my_vars):
    ''' Calculate CBS values for all COS '''
    if DEBUG:
        print ("Calculating CBS")
    if 'mtu_size' not in my_vars.keys():
        my_vars['mtu_size'] = 2004
    if 'RT_cbs_1' in my_vars.keys():
        my_vars['RT_cbs_1'] = int(calc_cbs(my_vars['RT_bandwidth_f1'], my_vars['mtu_size']))
    if 'INT_cbs_2' in my_vars.keys():
        my_vars['INT_cbs_2'] = int(calc_cbs(my_vars['INT_bandwidth_f2'], my_vars['mtu_size']))
    if 'ST_cbs_3' in my_vars.keys():
        my_vars['ST_cbs_3'] = int(calc_cbs(my_vars['ST_bandwidth_f3'], my_vars['mtu_size']))
    if 'BE_cbs_4' in my_vars.keys():
        my_vars['BE_cbs_4'] = int(calc_cbs(my_vars['BE_bandwidth_f4'], my_vars['mtu_size']))


def build_jinja2_template(template_file, my_vars, DEBUG):
    '''   Biuld the configuration by Rendering a Jinja2 configuration file  '''
    try:
        with open(template_file) as f1:
            cfg_template = f1.read()
        f1.close()
    except:
        print ("Could not Open Template, ", template_file)
    template_j2 = Environment(loader=BaseLoader).from_string(cfg_template)
    cfg_output = (template_j2.render(my_vars))
    cfg_output2 = "".join([s for s in cfg_output.strip().splitlines(True) if s.strip("\r\n").strip()])
    if DEBUG:
        print ("Render output based on my_vars and ", template_file)
        print (cfg_output2)
    return cfg_output2


def striprtf(text):


    ''' Strip out RTF data to produce a text file '''
    pattern = re.compile(r"\\([a-z]{1,32})(-?\d{1,10})?[ ]?|\\'([0-9a-f]{2})|\\([^a-z])|([{}])|[\r\n]+|(.)", re.I)
    # control words which specify a "destination".
    destinations = frozenset((
      'aftncn','aftnsep','aftnsepc','annotation','atnauthor','atndate','atnicn','atnid',
      'atnparent','atnref','atntime','atrfend','atrfstart','author','background',
      'bkmkend','bkmkstart','blipuid','buptim','category','colorschememapping',
      'colortbl','comment','company','creatim','datafield','datastore','defchp','defpap',
      'do','doccomm','docvar','dptxbxtext','ebcend','ebcstart','factoidname','falt',
      'fchars','ffdeftext','ffentrymcr','ffexitmcr','ffformat','ffhelptext','ffl',
      'ffname','ffstattext','field','file','filetbl','fldinst','fldrslt','fldtype',
      'fname','fontemb','fontfile','fonttbl','footer','footerf','footerl','footerr',
      'footnote','formfield','ftncn','ftnsep','ftnsepc','g','generator','gridtbl',
      'header','headerf','headerl','headerr','hl','hlfr','hlinkbase','hlloc','hlsrc',
      'hsv','htmltag','info','keycode','keywords','latentstyles','lchars','levelnumbers',
      'leveltext','lfolevel','linkval','list','listlevel','listname','listoverride',
      'listoverridetable','listpicture','liststylename','listtable','listtext',
      'lsdlockedexcept','macc','maccPr','mailmerge','maln','malnScr','manager','margPr',
      'mbar','mbarPr','mbaseJc','mbegChr','mborderBox','mborderBoxPr','mbox','mboxPr',
      'mchr','mcount','mctrlPr','md','mdeg','mdegHide','mden','mdiff','mdPr','me',
      'mendChr','meqArr','meqArrPr','mf','mfName','mfPr','mfunc','mfuncPr','mgroupChr',
      'mgroupChrPr','mgrow','mhideBot','mhideLeft','mhideRight','mhideTop','mhtmltag',
      'mlim','mlimloc','mlimlow','mlimlowPr','mlimupp','mlimuppPr','mm','mmaddfieldname',
      'mmath','mmathPict','mmathPr','mmaxdist','mmc','mmcJc','mmconnectstr',
      'mmconnectstrdata','mmcPr','mmcs','mmdatasource','mmheadersource','mmmailsubject',
      'mmodso','mmodsofilter','mmodsofldmpdata','mmodsomappedname','mmodsoname',
      'mmodsorecipdata','mmodsosort','mmodsosrc','mmodsotable','mmodsoudl',
      'mmodsoudldata','mmodsouniquetag','mmPr','mmquery','mmr','mnary','mnaryPr',
      'mnoBreak','mnum','mobjDist','moMath','moMathPara','moMathParaPr','mopEmu',
      'mphant','mphantPr','mplcHide','mpos','mr','mrad','mradPr','mrPr','msepChr',
      'mshow','mshp','msPre','msPrePr','msSub','msSubPr','msSubSup','msSubSupPr','msSup',
      'msSupPr','mstrikeBLTR','mstrikeH','mstrikeTLBR','mstrikeV','msub','msubHide',
      'msup','msupHide','mtransp','mtype','mvertJc','mvfmf','mvfml','mvtof','mvtol',
      'mzeroAsc','mzeroDesc','mzeroWid','nesttableprops','nextfile','nonesttables',
      'objalias','objclass','objdata','object','objname','objsect','objtime','oldcprops',
      'oldpprops','oldsprops','oldtprops','oleclsid','operator','panose','password',
      'passwordhash','pgp','pgptbl','picprop','pict','pn','pnseclvl','pntext','pntxta',
      'pntxtb','printim','private','propname','protend','protstart','protusertbl','pxe',
      'result','revtbl','revtim','rsidtbl','rxe','shp','shpgrp','shpinst',
      'shppict','shprslt','shptxt','sn','sp','staticval','stylesheet','subject','sv',
      'svb','tc','template','themedata','title','txe','ud','upr','userprops',
      'wgrffmtfilter','windowcaption','writereservation','writereservhash','xe','xform',
      'xmlattrname','xmlattrvalue','xmlclose','xmlname','xmlnstbl',
      'xmlopen',
    ))
    # Translation of some special characters.
    specialchars = {
      'par': '\n',
      'sect': '\n\n',
      'page': '\n\n',
      'line': '\n',
      'tab': '\t',
      'emdash': '\u2014',
      'endash': '\u2013',
      'emspace': '\u2003',
      'enspace': '\u2002',
      'qmspace': '\u2005',
      'bullet': '\u2022',
      'lquote': '\u2018',
      'rquote': '\u2019',
      'ldblquote': '\201C',
      'rdblquote': '\u201D',
    }
    stack = []
    ignorable = False       # Whether this group (and all inside it) are "ignorable".
    ucskip = 1              # Number of ASCII characters to skip after a unicode character.
    curskip = 0             # Number of ASCII characters left to skip
    out = []                # Output buffer.
    for match in pattern.finditer(text):
        word, arg, hex, char, brace, tchar = match.groups()
        if brace:
            curskip = 0
            if brace == '{':
                # Push state
                stack.append((ucskip,ignorable))
            elif brace == '}':
                # Pop state
                ucskip,ignorable = stack.pop()
        elif char: # \x (not a letter)
            curskip = 0
            if char == '~':
                if not ignorable:
                    out.append('\xA0')
            elif char in '{}\\':
                if not ignorable:
                    out.append(char)
            elif char == '*':
                ignorable = True
        elif word: # \foo
            curskip = 0
            if word in destinations:
                ignorable = True
            elif ignorable:
                pass
            elif word in specialchars:
                out.append(specialchars[word])
            elif word == 'uc':
                ucskip = int(arg)
            elif word == 'u':
                c = int(arg)
                if c < 0: 
                    c += 0x10000
                if c > 127: 
                    out.append(chr(c)) #NOQA
                else: 
                    out.append(chr(c))
                curskip = ucskip
        elif hex: # \'xx
            if curskip > 0:
                curskip -= 1
            elif not ignorable:
                c = int(hex,16)
                if c > 127: 
                    out.append(chr(c)) #NOQA
                else: 
                    out.append(chr(c))
        elif tchar:
            if curskip > 0:
                curskip -= 1
            elif not ignorable:
                out.append(tchar)
    return ''.join(out)


def read_service_variables(master, DEBUG):
    ''' Read in the Service Variables from either a RTF or YML file '''
    global yaml_str
    service_vars_file = master['service_vars'].split('.')[0] + str(j) +'.' + master['service_vars'].split('.')[1]
    service_vars_file_txt = master['service_vars'].split('.')[0] + str(j) +'.' + 'txt'
    service_vars_file_rtf = master['service_vars'].split('.')[0] + str(j) +'.' + 'rtf'
    if DEBUG:
        print(master)
    if master['service_file_type'].strip() == 'RTF':
        print("Converting RTF file ", service_vars_file_rtf, " into a YAML file")
        with open(service_vars_file_rtf, "r") as f21:
            lines = f21.read()
        f21.close()
        if DEBUG:
            print ("RTF...", lines, "...RTF")
            print("Debug removed")

        text = striprtf(lines)
        if DEBUG:
            print("TXT...", text, "...TXT")
        
        with open(service_vars_file_txt, 'w') as f22:
            yml_file = f22.write(text)
        f22.close()
        if DEBUG:
            print (service_vars_file_txt)
            print ("YML...", yml_file, "...YML")

        if DEBUG:
            print ("Reading Service Variable YAML file")
        with open(service_vars_file_txt) as tf:
            my_vars = yaml.load(tf)
        tf.close()
        
        

        
        
        if DEBUG:
            print ("myvars ...", my_vars, "...myvars")
    else:
        print ("Reading Service Variable YAML file")
        with open(service_vars_file) as tf:
            my_vars = yaml.load(tf)
        tf.close()
        if DEBUG:
            print ("myvars ...", my_vars, "...myvars")
    return my_vars


def directory_checks(directory1, directory2):
    ''' Check for Customer and VPN directories to be defined.   If not create them '''
    try:
        os.stat(directory1)
        print (directory1)
        try:
            os.stat(directory2)
        except:
            try:
                os.mkdir(directory2)
            except:
                print ("Could not create directories, make sure you have permission and are connected to file system")
    except:
        try: 
            os.mkdir(directory1)
            print ("make directory, ", directory1)
            try:
                os.stat(directory2)
            except:
                os.mkdir(directory2)
        except:
            print ("Could not create directories, make sure you have permission and are connected to file system")
        

#def main():
#'''Make it so.    This is the beginning of the main program section.'''
### Read the Master File
### Master file determines all the files and common variable needed to execute successfully"
master_file = "mrv_files.yml"
print ('\n 0. Reading Master File Variables \n')
with open(master_file) as mf:
    master = yaml.load(mf)
mf.close()
print ('... Master File loaded \n')


#If debug is set in the masterfile set a global debug variable
if 'DEBUG' in master.keys() and master['DEBUG'] is True:
    DEBUG = master['DEBUG']
else:
    DEBUG = False

j = 1   # counter for handling multiple service points
service_vars_file = master['service_vars'].split('.')[0] + str(j) +'.' + master['service_vars'].split('.')[1]
service_vars_file_txt = master['service_vars'].split('.')[0] + str(j) +'.' + 'txt'
service_vars_file_rtf = master['service_vars'].split('.')[0] + str(j) +'.' + 'rtf'

if DEBUG:
    print("SRV...", service_vars_file, "...SRV")

while os.path.isfile(service_vars_file) or os.path.isfile(service_vars_file_rtf):   
    ### From the service_vars_file_xxxx read in service variables.   All the variables in this file 
    ### file can be either in RTF or text (YML).
    ### Perform all request actions defined in the master dictionary.
    print('#' * 80)
    print ('\n 1. Reading in Service Variables for Location ID', j) 
    
    service_vars_file = master['service_vars'].split('.')[0] + str(j) +'.' + master['service_vars'].split('.')[1]
    service_vars_file_txt = master['service_vars'].split('.')[0] + str(j) +'.' + 'txt'
    service_vars_file_rtf = master['service_vars'].split('.')[0] + str(j) +'.' + 'rtf'
    master['service_file_type'] = master['service_file_type'].strip()
    
    if DEBUG:
        print("Service Site Location ID ", j)
        print("service_file_type #", master['service_file_type'], "#")

    my_vars = {}
    yaml_str = ""
    my_vars = read_service_variables(master, DEBUG)
    if DEBUG:
        print ("myvars ...", my_vars, "...myvars")
              
    mrv_template_file = master['mrv_template_file'] + "_" + my_vars['service_product'] + ".j2"
    pe_template_file = master['pe_template_file'] + "_" + my_vars['service_product'] + ".j2"
   
    if DEBUG:
        print (mrv_template_file)
        print (pe_template_file)
        
    # Ensure device name or optional IP address can be resolved.
    if 'edge_device' in my_vars.keys():
        device_name = my_vars['edge_device']
    if 'edge_ip' in my_vars.keys():
        IP = my_vars['edge_ip']
        try:
            device_ip = gethostbyname(IP)
        except:
            print("Bad IP for device specified")
            exit(1)
    elif 'edge_device' in my_vars.keys():
        device_name = my_vars['edge_device']
        try:
            device_ip = gethostbyname(device_name)
            my_vars['edge_ip'] = device_ip
            
        except:
            print("EDGE IP address not defined and hostname does not resolve to an IP")
            exit(0)
            
    if 'pe_device' in my_vars.keys():
        pe_device = my_vars['pe_device']
        try:
            pe_device_ip = gethostbyname(pe_device)
            my_vars['edge_ip'] = device_ip       
        except:
            print("PE IP address not defined and hostname does not resolve to an IP")
            exit(0)
            
            
        
    # define the proper device type that will be used by Netmiko.    For now the template only renders for MRV.   This will allow for future compatability.           
    if 'edge_device_type' in my_vars.keys():
        device_type = my_vars['edge_device_type']
        if my_vars['edge_device_type'] == 'mrv' or (my_vars['edge_device_type'] == 'cisco' and my_vars['edge_device_type'] <> 'juniper'):
            my_vars['edge_device_type'] = 'mrv_optiswitch'  
            device_type = 'mrv_optiswitch'      
    else:
        my_vars['edge_device_type'] = 'mrv_optiswitch'

    # make sure all the key variables are defined.    If not stop now.
    if not (('edge_ip' in my_vars.keys() or 'edge_device' in my_vars.keys()) 
            and (all(key in my_vars for key in ['s_vlan', 'customer_number', 'service_name', 'service-type', 'site_id', 's_ports', 'c_ports', 'edge_device_type', 'pe_customer_facing_interface', 'pe_device', 'L2VPLS_RD', 'L2VPLS_RT']))):
        print ("Not enough information to generate the configlets.")
        exit()          
    
    #determine all the file names that will be used for input, output, auditing
    my_vars['mrv_device'] = device_name
    mrv_service_file = my_vars['service_name'] + '-mrv-' + device_name + '-' + date.isoformat(date.today()) + '-' + str(j) + '.cfg'
    output_file = my_vars['service_name'] + '-birth-'  + date.isoformat(date.today()) + '.txt'
    err_file = my_vars['service_name'] + '-birth-'  + date.isoformat(date.today()) + '.err'
    output_file_path = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + output_file
    err_file_path = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + err_file
    mrv_file_path1 = master['file_path'] + my_vars['customer_number'] + "/" 
    mrv_file_path2 = master['file_path'] + my_vars['customer_number'] + "/" + my_vars['service_name'] + "/" + mrv_service_file
    directory1 = os.path.dirname(mrv_file_path1)
    directory2 = os.path.dirname(mrv_file_path2)
    if DEBUG:
        print(output_file_path)
    
    #if the customer directory does not exist create it. if the service directory does not exist create it.
    directory_checks(directory1, directory2)
    
    #This is turned off for now until this become production
    if DEBUG <> False:
        print ("\n Debug is Turned off, all output is being redirected to: \n 1. standard output : ", output_file_path, " \n 2. standard error :", err_file_path)
        sys.stderr.write(output_file_path)
        sys.stdout = open(output_file_path, 'w')
        sys.stderr = open(err_file_path, 'w')
    
    print ("\n 1.5 Performing checks if requested for ", my_vars['service_name'])
    if 'precheck_service' in master.keys() and master['precheck_service'] is True:
        print ("\n 1.5 Pre-flight checks")
        pre_check_pe_device( my_vars, iuser, PASSWORD2, DEBUG)
        pre_check_edge_device(my_vars, "admin", "mrv001", DEBUG)
        pre_check_agg_device(my_vars, iuser, PASSWORD2, DEBUG)
    
    print ("\n 2. Calculate Variables that are required within Python for Service, ", my_vars['service_name'])
    get_all_cbs_values(my_vars)
    
    print ('\n 3. Build the configuration based on the Jinja2 template for Service, ', my_vars['customer_number'], ",", my_vars['service_name'])
    copy_service_vars(j, master, my_vars, DEBUG) 
    render_edge_device(j, master, my_vars, DEBUG)     
    render_pe_device(j, master, my_vars, DEBUG)
    render_agg_devices(j, master, my_vars, DEBUG)

    print ('\n 4. Deploy Service if requested for EDGE, AGG, or PE for Service, ', my_vars['customer_number'], my_vars['service_name'], '\n')    
    if 'deploy_pe_service' in my_vars.keys() and master['deploy_pe_service'] is True:        
        print ('\n 4a. Provision changes on PE')
        status = upload_pe_device_configuration(j, master, my_vars, iuser, PASSWORD2, DEBUG)
        if not status:
            print("Upload not successful exiting")
            exit(1)
        
    if 'deploy_agg_service' in my_vars.keys() and master['deploy_agg_service'] is True:
        print ('\n 4b. Provision changes on aggswitches')
        #section to completed in the future.   Very similar to PE.

    if 'deploy_mrv_service' in my_vars.keys() and master['deploy_mrv_service'] is True:        
        print ('\n 4c. Provision changes on MRV')
        upload_edge_device_configuration(j, my_vars, mrv_file_path2, "admin", "mrv001", DEBUG)
    
    print ('\n 5. Test Services if requested from Service, ', my_vars['customer_number'], my_vars['service_name'], '\n')  
    if DEBUG:  
        print (master['test_service'])
    if 'test_service' in master.keys() and master['test_service'] is True:     
        print ("test Services")
        if 'service_ip' in my_vars.keys():
            if j == 1:
                test_ip = (my_vars['service_ip'].split(".")[0] + "." + my_vars['service_ip'].split(".")[1] + "." + my_vars['service_ip'].split(".")[2] + "." + "2")
            else:
                test_ip = (my_vars['service_ip'].split(".")[0] + "." + my_vars['service_ip'].split(".")[1] + "." + my_vars['service_ip'].split(".")[2] + "." + "1")
        else:
            test_ip = '355.1.1.1'
        print ("5.1 Testing PE")
        test_pe_device_service(my_vars, iuser, PASSWORD2, DEBUG)
        print ("5.2 Testing MRV")
        test_edge_device_service(my_vars, test_ip, "admin", "mrv001", DEBUG)
    
    j += 1
    if DEBUG:
        print (j, "end for")
    
    service_vars_file = master['service_vars'].split('.')[0] + str(j) +'.' + master['service_vars'].split('.')[1]
    service_vars_file_rtf = master['service_vars'].split('.')[0] + str(j) +'.' + 'rtf'

#if __name__ == "__main__":
#    main()
