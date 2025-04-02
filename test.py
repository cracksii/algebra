from solver import *
from variable import Variable

a = Variable()
b = Variable()

Variable.init(locals())

print(Variable.getbyname("a"))