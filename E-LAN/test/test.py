from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
from lxml import etree
#from lxml import raiseParseError
#import jinja2
#from jinja2 import Environment, BaseLoader
#import repr
from jnpr.junos.device import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
from ciscoconfparse import CiscoConfParse
from fileinput import close
from pprint import  pprint
from socket import gethostbyname
from socket import gethostbyaddr
import xml.etree.ElementTree as ET
import xmltodict 
from win32con import TECHNOLOGY
from getpass import getpass

def nslookitup(ip):
    try: 
        output = gethostbyaddr(ip)
        return output[0]
    except: 
        output = "not found" 
        return output


RT1 = '64512:65535'
RD1 = '65535'
RD2 = '10.92.6.61:65535'
axx_tech_rt = 4333
RT1 = '64512:1432'
RD2 = '10.92.6.21:4333'
VPN1 = 'AXX-TECH'
VPN_TYPE = "VPLS"
SID1 = int("503")
#axx_tech_rt = 4333
#RT1 = '64512:1210'
#RD2 = '10.92.6.7:3867'
#VPN1 = 'AHS-NET'
#VPN_TYPE = "VRF"
#SID1 = int("503")
print ("eg.  RT 64512:1432, RD 10.92.6.21:4333, SID = 503, VPN = AXX-TECH")

#PASSWORD = getpass()

iuser = raw_input("Juniper Username: ")
#print ("Username :" ,iuser)
PASSWORD2 = getpass()
PASSWORD2 = PASSWORD2.strip()
RT1 = raw_input("Route Target:  64512:xxxx # ")
RD2 = raw_input("Route Distinquisher 64512:xxxx or 10.92.x.x:xxxx  # ")
VPN1 = raw_input("VPN Name  # ")
SID1 = int(raw_input("Site Location ID for Layer 2 # "))

print ("Determining if RT exists, if so what are all the PEs participating in the VPN")
rr1_dev = Device(host='clgrab42mmrrf001', user=iuser, password=PASSWORD2, port=22)
#rr2_dev = Device(host='edtnabssmmrrf001', user=iuser, password=PASSWORD2, port=22)
rr1_dev.open()
#rr2_dev.open()
#print ("getting data from clgrab42mmrrf001")

route_target_rr1_data = rr1_dev.rpc.get_route_information({'format':'text'},table='bgp.rtarget')
route_l2vpn_rr1_data = rr1_dev.rpc.get_route_information({'format':'text'},table='bgp.l2vpn.0')
#print ("getting data from edtnabssmmrrf001")
#route_target_rr2_data = rr2_dev.rpc.get_route_information({'format':'text'},table='bgp.rtarget')
#route_l2vpn_rr2_data = rr2_dev.rpc.get_route_information({'format':'text'},table='bgp.l2vpn.0')
route_target_pe_cmd = 'show configuration routing-instances TEST-VPN' 
route_distinquisher_pe_cmd = 'show configuration routing-instances ' 
#route_target_pe_test = (dev.cli(route_target_pe_cmd))
#route_distinquisher_pe_test = (dev.cli(route_distinquisher_pe_cmd))
route_target_rr1_test = etree.tostring(route_target_rr1_data)
#route_target_rr2_test = etree.tostring(route_target_rr1_data)

route_l2vpn_rr1_test = etree.tostring(route_l2vpn_rr1_data)
#route_l2vpn_rr2_test = etree.tostring(route_l2vpn_rr2_data)
#print (route_l2vpn_rr_test)
rr1_dev.close()
#rr2_dev.close()
with open('rt1.txt', 'w') as rt1:
    rt1.write(route_target_rr1_test)
rt1.close()
#with open('rt2.txt', 'w') as rt2:
#    rt2.write(route_target_rr2_test)
#rt2.close()

with open('l2vpn1.txt', 'w') as l1:
    l1.write(route_l2vpn_rr1_test)
l1.close()
#with open('l2vpn2.txt', 'w') as l2:
#    l2.write(route_l2vpn_rr2_test)
#l2.close()




if VPN_TYPE == 'L2VPN' and SID1 > 2:
    print "Site ID should not be greater than 2 for L2VPNs"

l2rt1 = CiscoConfParse('rt1.txt')
l2rt1_objs = l2rt1.find_objects("64512:"+RT1+"/96")
#l2rt1_objs = l2rt1.find_objects(RD1)


ri_type = ""
site_exists = False
rd_exists = False
rt_exists = False
go_ahead = False
vpn_name_matches_RT = False


#print(l2vpn_objs1)+
rt1_pes = []
rt1_pes_names = []
for obj in l2rt1_objs:
    interface_name = obj.text
    #print (interface)
    if interface_name.find("64512:"+RT1+"/96") != -1:
        rt = interface_name.split(":")[1]+ ":" + interface_name.split(":")[2]
        rt_name = rt.split("/")[0]
        print("Route Target already defined: ",rt_name)
        for child in obj.all_children:
            if child.text.find("from") != -1:
                #print(child.text.split("from ")[1])
                
                rt1_pes.append(child.text.split("from")[1])
                pe_name = gethostbyaddr(child.text.split("from")[1])[0]
                rt1_pes_names.append(pe_name.split(".")[0])
    else:
        x = 0 
#print(rt1_pes)

if rt1_pes_names:
    rt_exists = True 
    rt1_pes_names.sort()
    print('RT defined on :',(rt1_pes_names))
else: 
    print ("There is no use of the RT")
#l2rt2 = CiscoConfParse('rt2.txt')ri_sid == SID1ri_sid == SID1
#l2rt2_objs = l2rt2.find_objects("64512:"+RT1+"/96")

#print(l2vpn_objs1)
#rt2_pes = []
#rt2_pes_names = []
#for obj in l2rt2_objs:
#    interface_name = obj.text
#    #print (interface)
#    if interface_name.find("64512:"+RT1+"/96") != -1:
#        rt = interface_name.split(":")[1]+ ":" + interface_name.split(":")[2]
#        rt_name = rt.split("/")[0]
#        print("Route Target already defined: ",rt_name)
#        for child in obj.all_children:
#            if child.text.find("from") != -1:
#                #print(child.text.split("from ")[1])
#                rt2_pes.append(child.text.split("from")[1])
#                rt2_pes_names.append(nslookitup(child.text.split("from")[1]))
#    else:
#        x = 0 
#print (rt2_pes)
#print(rt2_pes_names)


l2vpns1 = CiscoConfParse('l2vpn1.txt')
l2vpn_objs1 = l2vpns1.find_objects(RD2)

#print(l2vpn_objs1)
site1 = []
for obj in l2vpn_objs1:
    interface_name = obj.text
    #print (interface)
    if interface_name.find(RD2) != -1:
        rt = interface_name.split(":")[0]+ ":" + interface_name.split(":")[1] + ":" + interface_name.split(":")[2]  
        #print("Route Distinguisher already defined: ",rt)
        site1.append(interface_name.split(":")[2])  
    else:
        x = 0 
#print (site)

#l2vpns2 = CiscoConfParse('l2vpn2.txt')
#l2vpn_objs2 = l2vpns2.find_objects(RD2)
##print(l2vpn_objs2)
#site2 = []
#for obj in l2vpn_objs2:
#    interface_name = obj.text
#    #print (interface)

#    if interface_name.find(RD2) != -1:
#        rt = interface_name.split(":")[0]+ ":" + interface_name.split(":")[1] + ":" + interface_name.split(":")[2]  
#        #print("Route Distinguisher already defined: ",rt)
#        site2.append(interface_name.split(":")[2]) 
#    else:
#        x = 0 
#print (site )


print("/n/nShowing all the Site Instance for the VPN")
route_instance_dict = []
pe_sites = []
for pe_addr in rt1_pes_names:
    #print ("connecting to",pe_addr.split(".")[0])
    pe_name = pe_addr.split(".")[0]
    pe_dev = Device(host=pe_addr, user=iuser, password=PASSWORD2, port=22)
    pe_dev.open()
    route_instance_pe_cmd = 'show configuration routing-instances | display xml'
    route_instance_pe_test = (pe_dev.cli(route_instance_pe_cmd)) 
    route_instance_pe_result = etree.tostring(route_instance_pe_test)
    pe_dev.close()
    with open('ri.txt', 'w') as ri:
        ri.write(route_instance_pe_result)
    ri.close()
    
    with open('ri.txt') as fd:
        doc = xmltodict.parse(fd.read())
    fd.close()
    #print (doc)
    dic1 = doc['configuration']
    dic2 = dic1['routing-instances']
    #print (dic2)
    pe_sites_local = []
    ri_type= ""
    ri_sid = ""
    #dic1 = xmltodict(route_instance_pe_test)
    for dic3 in dic2['instance']:
        #print (dic3)
        if 'instance-type' in dic3.keys() and 'name' in dic3.keys() and 'route-distinguisher' in dic3.keys() and 'vrf-target' in dic3.keys():
            ri_rt = dic3['vrf-target']['community'].strip("target:")
            if ri_rt == RT1:
                vpn_name_matches_RT = True
                ri_type = dic3['instance-type']
                ri_name = dic3['name']
                ri_rd = dic3['route-distinguisher']['rd-type']
                if ri_rd == RD2:
                    rd_exists = True
                if ri_rd == RD2 and VPN1 == ri_name:
                   vpn_name_matches_RT = True
                ri_type = dic3['instance-type']
                #print (type(dic3['protocols']['vpls']['site']))
                if ri_type == 'vpls' and 'vpls' in (dic3['protocols'].keys()) and type(dic3['protocols']['vpls']['site']) == list:
                    #print ("found a list")
                    for dic4 in dic3['protocols']['vpls']['site']:
                        if 'vpls' in (dic3['protocols'].keys()): 
                            #print (dic4)
                            ri_sname = dic4['name']
                            ri_sid = int(dic4['site-identifier'])
                            #print (dic3['name'],dic3['route-distinguisher']['rd-type'],dic3['vrf-target']['community'].strip("target"))
                            #print (dic3['protocols']['vpls']['site']['name'],dic3['protocols']['vpls']['site']['site-identifier'])
                            pe_sites.append(ri_sid)
                            pe_sites_local.append(ri_sid)
                            ri_type = 'vpls'
                            print (pe_name,'vpn',ri_name,'rt',ri_rt,'rd',ri_rd,'site',ri_sname,'id',ri_sid)
                            if ri_rd == RD2 and VPN1 == ri_name and ri_sid == SID1:
                                site_exists = True
                                go_ahead = True
                                print ("RT Match, RD Match, VPN match, SID Match, means all good")
                            elif ri_sid == SID1:
                                site_exists = True
                                go_ahead = False
                                print ("Site does not match provided VPN, RT, RD")
                        elif 'l2vpn' in (dic3['protocols'].keys()):
                            #print (dic3['name'],dic3['route-distinguisher']['rd-type'],dic3['vrf-target']['community'].strip("target"))
                            #print (dic3['protocols']['l2vpn']['site']['name'],dic3['protocols']['l2vpn']['site']['site-identifier'])
                            ri_sname = dic4['name']
                            ri_sid = int(dic4['site-identifier'])
                            pe_sites.append(ri_sid)
                            pe_sites_local.append(ri_sid)
                            ri_type = 'vpls'
                            print (pe_name,'vpn',ri_name,'rt',ri_rt,'rd',ri_rd,'site',ri_sname,'id',ri_sid)
                            if ri_rd == RD2 and VPN1 == ri_name and ri_sid == SID1:
                                site_exists = True
                                go_ahead = True
                                print ("RT Match, RD Match, VPN match, SID Match, means all good")
                            elif ri_sid == SID1:
                                site_exists = True
                                go_ahead = False
                                print ("Site does not match provided VPN, RT, RD")
                elif 'vpls' in (dic3['protocols'].keys()): 
                    #print ("one Site for RD")
                    ri_sname = dic3['protocols']['vpls']['site']['name']
                    ri_sid = int(dic3['protocols']['vpls']['site']['site-identifier'])
                    #print (dic3['name'],dic3['route-distinguisher']['rd-type'],dic3['vrf-target']['community'].strip("target"))
                    #print (dic3['protocols']['vpls']['site']['name'],dic3['protocols']['vpls']['site']['site-identifier'])
                    pe_sites.append(ri_sid)
                    ri_type = 'vpls'
                    pe_sites_local.append(ri_sid)
                    print (pe_name,'vpn',ri_name,'rt',ri_rt,'rd',ri_rd,'site',ri_sname,'id',ri_sid)
                    if ri_rd == RD2 and VPN1 == ri_name and ri_sid == SID1:
                        site_exists = True
                        go_ahead = True
                        print ("RT Match, RD Match, VPN match, SID Match, means all good")
                    elif ri_sid == SID1:
                        site_exists = True
                        go_ahead = False
                        print ("Site does not match provided VPN, RT, RD")
                elif 'l2vpn' in (dic3['protocols'].keys()):
                    #print ("one site for RD")
                    #print (dic3['name'],dic3['route-distinguisher']['rd-type'],dic3['vrf-target']['community'].strip("target"))
                    #print (dic3['protocols']['l2vpn']['site']['name'],dic3['protocols']['l2vpn']['site']['site-identifier'])
                    ri_sname = dic3['protocols']['l2vpn']['site']['name']
                    ri_sid = int(dic3['protocols']['l2vpn']['site']['site-identifier'])
                    pe_sites.append(ri_sid)
                    pe_sites_local.append(ri_sid)
                    ri_type = 'vpls'
                    
                    print (pe_name,'vpn',ri_name,'rt',ri_rt,'rd',ri_rd,'site',ri_sname,'id',ri_sid)
                    if ri_rd == RD2 and VPN1 == ri_name and ri_sid == SID1:
                        site_exists = True
                        go_ahead = True
                        print ("RT Match, RD Match, VPN match, SID Match, means all good")
                    elif ri_sid == SID1:
                        site_exists = True
                        go_ahead = False
                        print ("Site does not match provided VPN, RT, RD")
                elif ri_type == 'vrf':
                    print (pe_name,'vpn',ri_name,'rt',ri_rt,'rd',ri_rd)
    #if ri_type == 'vpls' or ri_type == 'l2vpn':
    #    print sorted(pe_sites_local,reverse=True)
if rt1_pes_names:   #make sure the list is not empty
    if ri_type == 'vpls' or ri_type == 'l2vpn':
        print ("There are ",len(pe_sites), "site identifiers, they are: ", sorted(pe_sites,reverse=True))
    else: 
        print ("There is no use of the RT, you can safely use this RT for a new VPN")
        
    
    #route_instance_dict.append(route_instance_pe_result)

else:
    print ("Check the VPN, RT, RD, or site id")  
if site_exists == False:
    
    print ("Site ID is unique across the Whole VPN for a new connection")
if go_ahead:
    print ("All is good to on the PE side of the house")
    
ri_type = ""
site_exists = False
rd_exists = False
rt_exists = False
vpn_name_matches_RT = False   
    
    





