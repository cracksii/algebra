import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from threaded_grid import threaded_solutions
from variable import Variable
from term import Term
from functions import *

ax = plt.axes()
x = Variable()
y = Variable()
Variable.init(locals())

points1 = threaded_solutions(3*sin(x)-y, Term(0), 0, width=500, lines=100)
#points2 = threaded_solutions(0.02*x**4-x**2+6, Term(y), 0, width=50, lines=100)

print(len(points1))

for i in points1:
    ax.scatter(i[x], i[y], c="blue", s=10)

plt.show()


