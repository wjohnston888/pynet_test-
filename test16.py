class NetworkDevice(object):
#def inside a function is a method   
#   __init__ is a special function when a object instance is created.
#   assign parameters to the object
#   first thing is the reference to the object ie. my_obj
    def __init__(self, ip, username, password):   #ip, username, password parameters
        self.ip = ip  #ip is the name of the attribute
        self.username = username
        self.password = password


class SomeClass(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def sum(self):
        return self.x + self.y
    def prod(self):
        return self.x * self.y

class NewClass(SomeClass):
    def __init__(self,x,y,z):
        SomeClass.__init__(self,x,y)
        self.z = z 
    def sum(self):
        return self.x + self.y + self.z
    def prod(self):
        return self.x * self.y * self.z
        

rtr3 = NetworkDevice('10.1.1.1','admin','passwd')
rtr4 = NetworkDevice('10.1.1.2','admin2','passwd2')
a = SomeClass(3,7)
b = NewClass(8,9,10)
