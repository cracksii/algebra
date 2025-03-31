from term import Term
from variable import Variable
from math import isnan
from numpy import linspace
from watch import watch
from random import shuffle

MAX_ITERATIONS = 1000
ACCURACY = 10
DEBUG = False
H = (1 / (10**(ACCURACY)))


class Iteration:
    def __init__(self, x, y, d, s):
        self.x = float(x)          # x value of iteration
        self.y = float(y)          # y value of iteration
        self.derivative = float(d) # derivative of the function at x
        self.delta = float(s)      # delta
        self.r = False

    def __str__(self):
        if self.r:
            return f'<x: {round(self.x, ACCURACY)}, y: {round(self.y, ACCURACY)}, d: {round(self.derivative, ACCURACY)}, s: {round(self.delta, ACCURACY)}>'
        return f'<x: {self.x}, y: {self.y}, d: {self.derivative}, s: {self.delta}>'

    __repr__ = __str__


class MultiIteration:
    def __init__(self, vals, var, y, d, s):
        self.vals = vals.copy()
        self.var = var
        self.y = y
        self.derivative = d
        self.delta = s
        self.r = True

    def __str__(self):
        if self.r:
            return f"<{Variable.getname(self.var)}: {round(self.vals[self.var], ACCURACY)}, out: {round(self.y, ACCURACY)}, d: {round(self.derivative, ACCURACY)}, s: {round(self.delta, ACCURACY)}, vals: {self.vals}>"
        return f"<{self.var}: {self.vals[self.var]}, out: {self.y}, d: {self.derivative}, s: {self.delta}, vals: {self.vals}>"

    def x(self):
        return self.vals[self.var]

    __repr__ = __str__


def calc_derivative(f, x, y):
    # Calculate the derivative
    derivative = ((f.compute(x + H) - y).real / H - ((f.compute(x - H) - y).real / H)) / 2
    k = H

    # Derivative must not be zero
    while derivative == 0:
        k *= 10

        # Worse approximation for the derivative, which hopefully is not zero
        if x > 0 or x == 0:
            derivative = (f.compute(x + k) - y).real / k
        else:
            derivative = -(f.compute(x - k) - y).real / k
    return derivative


def solve(term1, term2, start=None):
    if not start:
        start = 1

    if isinstance(term1, Variable):
        term1 = Term(term1)
    if isinstance(term2, Variable):
        term2 = Term(term2)

    assert isinstance(term1, Term)
    term1 = term1.clone()


    if isinstance(term2, Term):
        term2 = term2.clone()
    
    x = start                   # Starting value
    steps = []                  # Keeps track of past computations
    num = MAX_ITERATIONS

    f = term1 - term2

    # Calculates a new x value for the next iteration
    def delta():
        # print(steps, -steps[-1].y / steps[-1].derivative)
        
        # Return better x approximation based on y difference and derivative at x
        return -steps[-1].y / steps[-1].derivative

    while num > 0:
        y = f.compute(x)

        # Checks if x is inside the domain of definition
        if isinstance(y, float) and isnan(y):
            x += 1
            continue
        
        derivative = calc_derivative(f, x, y)

        # Stores the most recent step for the next x value computation
        steps.append(Iteration(x, y.real, derivative, 0))

        # Checks if newly computed x is a solution for the equation
        if y == 0 or abs(y) < H:
            return float(round(x, ACCURACY))
        else:
            d = delta()
            x += d
            steps[-1].delta = d

        if DEBUG:
            print(steps[-1])

        num -= 1

    return float('nan')


def nn_derivative(f, vals, var, y):
    # Calculate the derivative
    cpy1 = vals.copy()
    cpy2 = vals.copy()
    cpy1[var] += H
    cpy2[var] -= H
    derivative = ((f.compute(cpy1) - y).real / H - ((f.compute(cpy2) - y).real / H)) / 2
    k = H
    # Derivative must not be zero
    iterations = 10
    while round(derivative, ACCURACY - 1) == 0:
        iterations -= 1
        k *= 10
        cpy1 = vals.copy()
        cpy2 = vals.copy()
        cpy1[var] += k
        cpy2[var] -= k
        # Worse approximation for the derivative, which hopefully is not zero
        if vals[var] > 0 or vals[var] == 0:
            derivative = (f.compute(cpy1) - y).real / k
        else:
            derivative = -(f.compute(cpy2) - y).real / k
        if iterations == 0:
            return None
    return derivative

#@watch
def nn_solve(f, vals, var):
    steps = []                  # Keeps track of past computations
    num = 20

    # Calculates a new x value for the next iteration
    def delta():
        # print(steps, -steps[-1].y / steps[-1].derivative)
        
        # Return better x approximation based on y difference and derivative at x
        return -steps[-1].y / steps[-1].derivative

    while num > 0:
        y = f.compute(vals)

        # Checks if x is inside the domain of definition
        if isinstance(y, float) and isnan(y):
            vals[var] += 1
            continue
        
        derivative = nn_derivative(f, vals, var, y)
        if derivative == None:
            return float("nan"), num

        # Stores the most recent step for the next x value computation
        #steps.append(Iteration(vals[var], y.real, derivative, 0))
        steps.append(MultiIteration(vals, var, y, derivative, 0))

        # Checks if newly computed x is a solution for the equation
        if y == 0 or abs(y) < H:
            return float(round(vals[var], ACCURACY)), num
        else:
            d = delta()
            vals[var] += d
            steps[-1].delta = d

        num -= 1
    if num != 0:
        minimum = min([abs(_.y) for _ in steps])
        for iteration in steps:
            if abs(iteration.y) == minimum:
                return round(iteration.x(), ACCURACY), num

    return float("nan"), num

#@watch
def solve_multi(term1, term2, start_vals=None):
    term1 = Term(term1).clone()
    term2 = Term(term2).clone()
    variables = [_ for _ in term1.variables] + [_ for _ in term2.variables if _ not in term1.variables]
    if not start_vals:
        start_vals = {a: 1 for a in variables}
    
    start_vals = {a: b for a, b in start_vals.items() if a in variables}
    vals = start_vals.copy()
    shuffle(variables)

    f = term1 - term2
    iterations = 50
    if DEBUG:
        print(vals, f.compute(vals))
    while True:
        iterations -= 1
        num = MAX_ITERATIONS
        for var in variables:        
            vals[var], num = nn_solve(f, vals, var)
            if DEBUG:
                print(var.selfname(), vals, f.compute(vals))
            if num > 0:
                break
        if num > 0 or iterations == 0:
            break
    if iterations == 0 or num == 0:
        return None
    return vals


@watch
def multi_solutions(term1, term2, start, width=10, lines=200):
    solved = solve_multi(term1, term2, start)
    solutions = [solved]
    grid = []
    for i in solved.keys():
        grid.append(list(linspace(solved[i]-width/2, solved[i]+width/2, lines)))
        
    # We could generate a list which contains every point in the grid, but going up with dimensions it would take too much RAM

    idxs = [0 for _ in range(len(solved))]


    while True:
        vals = {}
        for i, v in enumerate(idxs):
            vals[list(solved.keys())[i]] = grid[i][v]

        solution = solve_multi(term1, term2, vals)
        if solution not in solutions:
            solutions.append(solution)

        if sum(idxs) == (lines - 1) * len(idxs):
            break
        idxs[-1] += 1
        if idxs[-1] == lines:
            new_idxs = []
            next_p1 = False
            for i in reversed(idxs):
                if next_p1:
                    i += 1
                    next_p1 = False
                if i == lines:
                    new_idxs.append(0)
                    next_p1 = True
                    continue
                new_idxs.append(i)
            idxs = [_ for _ in reversed(new_idxs)]

    return solutions


def equation_system(eqs): # eqs is a list of tuples with two terms representing the left and right side of an equations
    TOLERANCE = 1e-5
    from threaded_grid import threaded_solutions
    for i in eqs:
        assert len(i) == 2
        i = (Term(i[0]), Term(i[1]))

    valid_solutions = []
    start = None
    width = 1000
    lines = 100
    while len(valid_solutions) == 0:
        solutions = [[] for _ in eqs]    
        for idx, eq in enumerate(eqs):
            solutions[idx] = threaded_solutions(eq[0], eq[1], start, width, lines)
        
        # print(len(solutions), [len(_) for _ in solutions if _])
        variables = []
        for i in solutions:
            for k in i[0].keys():
                if k not in variables:
                    variables.append(k)
        
        minimum_delta = {k: float("inf") for k in variables}

        print(f"Last solutions {solutions[0][0]} {solutions[0][int(len(solutions[0])/2)]} {solutions[0][-1]}")
        print("\n")
        for idx, solution_set1 in enumerate(solutions):
            for idx2, solution_set2 in enumerate(solutions):
                if idx == idx2:
                    continue

                for s1 in solution_set1:
                    for s2 in solution_set2:
                        if s1 == s2:
                            valid_solutions.append((s1, s2))
                        
                        keys = [_ for _ in s1.keys() if _ in s2.keys()]
                        valid = True
                        for k in keys:
                            if abs(s1[k] - s2[k]) < minimum_delta[k]:
                                minimum_delta[k] = abs(s1[k]-s2[k])
                                if not start:
                                    start = {}
                                start[k] = (s1[k] + s2[k]) / 2
                                #print(k, s1[k] - s2[k], start, s1, s2)


                            if abs(s1[k] - s2[k]) >= TOLERANCE:
                                valid = False
                                break
                        if valid:
                            valid_solutions.append((s1, s2))

        if len(valid_solutions) == 0:
            width /= 10
    
    return_solutions = []
    for v in valid_solutions:
        return_solutions.append([])
        for i in v:
            cpy = {}
            for k in i.keys():
                cpy[k] = round(i[k], ACCURACY)
            return_solutions[-1].append(cpy)

    
    for i in return_solutions:
        print(i)
    return return_solutions
