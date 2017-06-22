#!/usr/bin/env python
from __future__ import print_function
from getpass import getpass
from pprint  import pprint
from netmiko import ConnectHandler

def save_file(filename, show_run):
    """Save the show run to a file"""
    with open(filename, "w") as f:
        f.write(show_run)

def main():
    """Exercises using Netmiko"""
    password = getpass()
    pynet_rtr1 = {
        'device_type': 'cisco_ios',
        'ip':   '184.105.247.70',
        'username': 'pyclass',
        'password': password,
    }

    pynet_srx = {
        'device_type': 'juniper_junos',
        'ip':   '184.105.247.76',
        'username': 'pyclass',
        'password': password,
    }


    for dev in (pynet_rtr1, pynet_srx):
        net_connect = ConnectHandler(**dev)
        print("Current Prompt: " + net_connect.find_prompt())
        show_ver = net_connect.send_command("show version")
        print()
        print('#' * 80)
        pprint(show_ver) 
        print() 
        print('#' * 80)
        if 'cisco' in show_ver:
            cmd = "show run"
        elif 'JUNOS' in show_ver:
            cmd = "show configuration"
        show_run = net_connect.send_command(cmd)
        filename = net_connect.base_prompt + ".txt"
        print ("Save config output: {}\n".format(filename))
        save_file(filename, show_run)

if __name__ == "__main__":
    main()
