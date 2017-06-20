f = open("workfile.txt")
output = open("outputfile.txt","w")
lines = f.readlines()
print (f)
count = len(lines)
print("-" * 60)
for line in lines:
    print line.strip()

output.write("whatever\n")
f.close()

