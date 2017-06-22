#!/usr/bin/env python
"""Exercises using Netmiko"""
from __future__ import print_function
from getpass import getpass
from netmiko import ConnectHandler

def read_yml_file(filename):
    """Read YAML file"""
    with open(filename) as f:
        return yaml.load(f)



def main():
    """Exercises using Netmiko"""
    passwd = getpass("Enter password: ")


    cfg_commands = [
        'set system syslog file messages any error',
    ]

    filename = "my_device.yml"
    devices = read_yml_file(filename)
    password = getpass()

    for dev in devices:
        net_connect = ConnectHandler(**dev)
        print("Current Prompt: " + net_connect.find_prompt())

        print("\nConfiguring Syslog + commit")
        print("#" * 80)
        output = net_connect.send_config_set(cfg_commands)
        output += net_connect.commit()
        print(output)
        print("#" * 80)
        print()


if __name__ == "__main__":
    main()
