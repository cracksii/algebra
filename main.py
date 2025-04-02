from variable import Variable 
from solver import *
from threaded_grid import threaded_solutions
from functions import *

def main():

    x = Variable()
    y = Variable()
    z = Variable()
    Variable.init(locals())

    #eq = 6-0.2*(x**4+y**4)
    #eq2 = 3
    

    # 3x = 4 => x = 4/3

    # 3x = y
    # 1-y = 2-x <=> 1+x=2+y <=> y=x-1
    # 3x = x-1 <=> x=-1/2 => y=-3/2

    #print(solve_multi(1-y, 2-x, start_vals={x: 1, y:1}))
    #print(solve_multi(3*x, 0, start_vals={x: 1, y:1}))
    # print(threaded_solutions(1-y, 2-x, {x:10, y:10}))
    #equation_system([(3*x, z), (1-z, 2*y), (z, 3)])
    equation_system((y, 4 * sin(x)), (y, 3))


if __name__ == "__main__":
    main()

