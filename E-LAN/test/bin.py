
    

j1 = 1
i1 = 1
bit1 = 0
found1 = False
found2 = False
valid_vlan = False
#find first significant bit
VLAN1 = raw_input("VLAN 1 :")
VLAN2 = raw_input("VLAN 2 :")

range = VLAN1 + " up-to " + VLAN2
v1 = int(range.split("up-to")[0])
v2 = int(range.split("up-to")[1])
rv = v2-v1
x=v1

print ("{0:b}".format(v1))
print ("{0:b}".format(v2))
print ("{0:b}".format(v1&v2))
if v1 % 2 <> 0:
    print ("for a range first VLAN must be divisible by two")
if v2 % 2 <> 1:
    print ("for a range 2nd VLAN must not be divisible by two")
if v2 < v1:
    print("VLAN 2 must be greater than V1")
if (v1 & v2) <> v1:  #if you and both v1 and v2 you should get v1.
    print("No Valid Binary boundary")



#if (rv for rvs in [1,3,7,31,63,127,255,511,1023,2047,4095]
#(all(key in my_vars for key in ['s_vlan','customer_number','s
#if 
while i1 < 12  and not found1:
    y = x  >>  i1
    #print ("{0:b}".format(y))

    if x& (1<<i1)  != 0 and not found1:
        found1 = True
        bit1 = i1
        #print ("Found",i1,'bits')
        #clear_bit = x & ~(1 << (i1 - 1)
        #print ("{0:b}".format(clear_bit))
    i1 = i1 + 1
j = 1
if i1==12 and not found1:
    bit1 = 12
while j <= bit1:
    #print ("Range ",2**j-1)
    if (v2 == v1 + 2**j -1 ):
        valid_vlan = True
    j = j + 1
       
if valid_vlan:
    print ("Valid range")
else:
    print ("Not a valid range.   Needs to be on a Binary Boundary, mask needs to be within ",bit1,"bits")
    



