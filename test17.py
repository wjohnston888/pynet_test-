from pprint import pprint
f = open("show_arpt.txt")
show_arp = f.readlines()

arp_dict = {}

for line in show_arp:
    if 'Protocol' is in line:
        continue
    line = line.strip()
    fields = line.split()
    ip_addr = fields[1]
    mac_addr = fields[3]
    atrp_dict[ip_addr] = mac_addr
    pprint(arp_dict)


reserve_arp - {}
for k,v in arp_dict.items():
    reverse_arp[mac_addr] = arp_dict.items[ip_addr]


