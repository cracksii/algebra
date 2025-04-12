from term import Term
from variable import Variable
from math import isnan
from numpy import linspace
from watch import watch
from random import shuffle
from time import time
from itertools import groupby

import matplotlib.pyplot as plt


MAX_ITERATIONS = 1000
ACCURACY = 6
DEBUG = True
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


def nn_solve(f, vals, var):
    steps = []                  # Keeps track of past computations
    num = 50

    # Calculates a new x value for the next iteration
    def delta():
        # print(steps, -steps[-1].y / steps[-1].derivative)
        
        # Return better x approximation based on y difference and derivative at x
        return -steps[-1].y / steps[-1].derivative
    
    #sta = time()
    while num > 0:
        num -= 1
        #print(time() - sta, len(steps))
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

    if num != 0:
        minimum = min([abs(_.y) for _ in steps])
        for iteration in steps:
            if abs(iteration.y) == minimum:
                return round(iteration.x(), ACCURACY), num

    return float("nan"), num


def solve_multi(term1, term2, start_vals=None):
    term1 = Term(term1).clone()
    term2 = Term(term2).clone()
    f = term1 - term2
    variables = f.variables

    if not start_vals:
        start_vals = {a: 1 for a in variables}

    start_vals = {a: b for a, b in start_vals.items() if a in variables}
    vals = start_vals.copy()
    shuffle(variables)

    iterations = 5
    while iterations > 0:
        iterations -= 1
        num = MAX_ITERATIONS
        for var in variables:
            new_val, num = nn_solve(f, vals, var)
            vals[var] = new_val
            if num > 0:
                break
        if num > 0:
            break
    #print(iterations, num, f, start_vals, vals, flush=True, end="\n\n")
    if iterations == 0 or num == 0:
        return None
    return vals


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


class HashableDict(dict):
    def __hash__(self):
        # print(sum([hash(_) for _ in self._keys]) + sum([hash(_) for _ in self._values]))
        return hash(str(self.keys()) + str(self.values()))
    
class HashableSet(frozenset):
    def __repr__(self):
        out = "<"
        solutions = self.list()
        for i in solutions:
            i.print_term = False
            out += f"{i}, "
            i.print_term = True
        return out[:-2] + ">"
    
    def __getitem__(self, item):
        return self.list()[item]

    def list(self):
        return list(sorted(self, key=lambda x: x.term))

    def same_vars(self):
        variables = []
        var_refs = []
        for i in self.list():
            variables.append(i.vars())
            for k in variables[-1]:
                if k not in var_refs:
                    var_refs.append(k)
    
        rm = []
        for var in var_refs:
            for eq_vars in variables:
                if var not in eq_vars:
                    rm.append(var)
                    break
        for i in rm:
            var_refs.remove(i)
        return var_refs

@watch
def equation_system(*eqs):
    TOLERANCE = 1 / (10 ** ACCURACY)
    from threaded_grid import threaded_solutions
    
    for i in eqs:
        assert len(i) == 2
        i = (Term(i[0]), Term(i[1]))

    valid_solutions = []
    width = 1000
    lines = 100
    search_values = [None]
    max_iterations = MAX_ITERATIONS

    while len(valid_solutions) == 0:    # It should be "while len(potential_solutions) > 0 (ensures all potential solutions are found) or potential_solutions == None (startcase)"
        max_iterations -= 1
        if max_iterations == 0:
            break
        
        for sidx, search in enumerate(search_values):
            solutions = [[] for _ in eqs]    
            for idx, eq in enumerate(eqs):
                solutions[idx] = threaded_solutions(eq[0], eq[1], search, width, lines)
                if len(solutions[idx]) == 0:
                    print(f"The system cannot be solved due to equation: {eq}, which has no (real) solutions")
                    return
            
            unique_solutions_set = set()
            filtered_solutions = []
            for sol_list in solutions:
                unique_sol_list = []
                for sol in sol_list:
                    rounded_sol = frozenset({k: round(sol[k], ACCURACY - 1) for k in sol}.items())
                    if rounded_sol not in unique_solutions_set:
                        unique_solutions_set.add(rounded_sol)
                        dct = HashableDict()
                        dct.update(sol.items())
                        unique_sol_list.append(dct)
                filtered_solutions.append(unique_sol_list)
            print("original / filtered", [len(_) for _ in solutions if _], [len(_) for _ in filtered_solutions if _], end="\n\n\n", flush=True)
            solutions = filtered_solutions

            variables = list({k for sol in solutions for s in sol for k in s.keys()})
            minimum_delta = {k: float("inf") for k in variables}
            deltas = HashableDict()
            for idx, solution_set1 in enumerate(solutions):
                for idx2, solution_set2 in enumerate(solutions):
                    if idx == idx2:
                        continue
                    
                    for s1 in solution_set1:
                        for s2 in solution_set2:
                            if s1 == s2:
                                valid_solutions.append((s1, s2))
                                continue
                            sol_set = HashableSet({s1, s2})
                            if sol_set not in deltas.keys():
                                deltas[sol_set] = 0
                            keys = [_ for _ in s1.keys() if _ in s2.keys()]
                            valid = True
                            for idx, k in enumerate(keys):
                                S_k = max(1, 0.5 * (abs(s1[k]) + abs(s2[k]))) 
                                deltas[sol_set] += abs(s1[k] - s2[k]) / S_k  
                                #print(abs(s1[k] - s2[k]), (s1, s2))
                                if abs(s1[k] - s2[k]) < minimum_delta[k]:
                                    minimum_delta[k] = abs(s1[k] - s2[k])
                                    if not search_values[sidx]:
                                        search_values[sidx] = {}
                                    search_values[sidx][k] = (s1[k] + s2[k]) / 2
                                if abs(s1[k] - s2[k]) >= TOLERANCE:
                                    valid = False
                            if valid:
                                valid_solutions.append((s1, s2))

            if False:
                ax = plt.axes()
                for k, v in deltas.items():
                    if abs(v) > 3.84:
                        continue
                    for i in list(k):
                        if Variable.getbyname("x") in i.keys():
                            ax.scatter(abs(i[Variable.getbyname("x")] + i[Variable.getbyname("y")]), v)
                plt.show()


            # Calculate potential solutions and identify doubles 
            delta_vals = sorted(deltas.values())
            top_solutions = [(i, list(deltas.keys())[list(deltas.values()).index(i)]) for i in delta_vals[:10]]
            rm = []
            for idx1, (delta1, s1) in enumerate(top_solutions):
                for idx2, (delta2, s2) in enumerate(top_solutions):
                    if idx1 == idx2:
                        continue
                    if abs(delta1 - delta2) < TOLERANCE and max(delta1, delta2) not in rm:
                        rm.append(max(delta1, delta2))

            for r in rm:
                top_solutions.remove([_ for _ in top_solutions if _[0] == r][0])


            
            if True:
                varx = Variable.getbyname("x")
                vary = Variable.getbyname("y")
                for st in solutions:
                    ax = plt.axes()
                    for solution in st:
                        ax.scatter(solution[varx], solution[vary])
                    print(len(st))
                    plt.show()
            
            for k in top_solutions:
                print(k)
            return

        if len(valid_solutions) == 0:
            width /= 10
    
    unique_solutions = set()
    return_solutions = []
    
    for v in valid_solutions:
        rounded_pair = tuple(
            frozenset({k: round(v[i][k], ACCURACY - 3) for k in v[i]}.items())
            for i in range(len(v))
        )
        sorted_pair = tuple(sorted(rounded_pair))
        
        if sorted_pair not in unique_solutions:
            unique_solutions.add(sorted_pair)
            return_solutions.append([{k: v for k, v in pair} for pair in tuple(
                frozenset({k: round(v[i][k], ACCURACY - 1) for k in v[i]}.items())
                for i in range(len(v))
            )])

    for sol in return_solutions:
        print(sol)
    
    return return_solutions


def calculate_solutions(eqs):
    from threaded_grid import threaded_solutions
    from math import sqrt

    all_solutions = []
    for idx, (eq1, eq2) in enumerate(eqs):
        solutions = threaded_solutions(eq1, eq2, None, 1000, 100)
        for i in range(len(solutions)):
            solutions[i].term = idx

        if len(solutions) == 0:
            print("Not solvable")
            return None

        solutions = sorted(solutions, key=lambda x: sqrt(sum([_**2 for _ in x.values()])))
        all_solutions.append(solutions)
    return all_solutions


@watch
def equation_system2(*eqs):
    """
    Solve a system of given equations

    :param *eqs The set of equations to solve (left_side, right_side), (left_side2, right_side2)...
    """
    from itertools import product
    from threaded_grid import Solution

    all_solutions = calculate_solutions(eqs)
    print([len(_) for _ in all_solutions])

    # Calculate delta values for potential solutions of the system
    for idx1 in range(len(all_solutions)-1):                            # This ensures every solutions set is paired with every other only ONCE and never with itself
        print(idx1, idx1+1)
        for idx2 in range(idx1 + 1, len(all_solutions)):
            if idx1 == idx2:
                continue
            deltas = {}
            for s1, s2 in product(all_solutions[idx1], all_solutions[idx2]):
                mutual_keys = [_ for _ in s1.keys() if _ in s2.keys()]
                if len(mutual_keys) == 0:                               # Cannot solve independent equations
                    break
                key = HashableSet({s1, s2})                             # Key is a set, because its irrelevant which equations is s1 and which is s2

                deltas[key] = 0
                for k in mutual_keys:
                    delta = abs(s1[k] - s2[k])                          # Probably need to adjust delta calculation
                    deltas[key] += delta

    best_deltas = {_: list(deltas.keys())[list(deltas.values()).index(_)] for _ in sorted(deltas.values())[:10]}
    items = list(best_deltas.items())
    
    for k, v in best_deltas.items():
        print(k, v)

    # 

