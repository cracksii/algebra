from threading import Thread
from solver import *
from numpy import linspace
from watch import watch


class Thr(Thread):
    def __init__(self, points, idx, t1, t2):
        super().__init__(None, None, None, (), {})
        self.grid_points = points
        self.t1 = t1
        self.t2 = t2
        self.solutions = []
        self.idx = idx


    def run(self):
        #print(f"{self.idx} started")
        for pt in self.grid_points:
            solution = solve_multi(self.t1, self.t2, pt)
            #print(f"{self.idx} solved pt {self.grid_points.index(pt)}/{len(self.grid_points)}")
            if not solution:
                continue
            if solution not in self.solutions:
                self.solutions.append(solution)
        #print(f"{self.idx} finished")

    def join(self):
        super().join()
        #print(f"{self.idx} joined")
        return self.solutions


class Solution(dict):
    print_term = True
    term = None
    
    def __hash__(self):
        return hash(str(self.keys()) + str(self.values()))
    
    def vars(self):
        return sorted([_ for _ in self.keys() if isinstance(_, Variable)], key=lambda x: x.selfname())
    
    def __repr__(self):
        out = ""
        for v in self.vars():
            out += f"{v}:{self[v]}, "
        out = out[:-2] + "}"
        if self.term is not None and self.print_term:
            return "{idx: " + str(self.term) + ", " + out
        else:
            return "{" + out


def threaded_solutions(term1, term2, start, width=10, lines=400):
    solved = solve_multi(term1, term2, start)
    
    solutions = [solved]
    grid = []
    if isinstance(start, float) or isinstance(start, int):
        start = {_: start for _ in term1.variables + [_ for _ in term2.variables if _ not in term1.variables]}
    if not start:
        start = {}
    for k in solved:
        if k not in start.values():
            start[k] = solved[k]
    #print(start, solved, flush=True)
    for i in solved.keys():
        grid.append(list(linspace(start[i]-width/2, start[i]+width/2, lines)))
    print(f"solution info{[(i, solved[i], min(linspace(solved[i]-width/2, solved[i]+width/2, lines)), max(linspace(solved[i]-width/2, solved[i]+width/2, lines))) for i in solved.keys()]}")
    # We could generate a list which contains every point in the grid, but going up with dimensions it would take too much RAM

    idxs = [0 for _ in range(len(solved))]

    grid_points = []
    while True:         # Generate the grid points for the threads --- Better approach: Calculate total number of points: t_n_p = lines ^ numVariables
        vals = {}       #                                              Generate t_n_p / num_threads points - dispatch thread with those points - continue with next thread
        for i, v in enumerate(idxs):
            vals[list(solved.keys())[i]] = grid[i][v]

        grid_points.append(vals)

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

    num_thr = 8
    thread_points = []
    length = len(grid_points)
    for i in range(num_thr):
        if i == num_thr - 1:
            thread_points.append(grid_points)
            grid_points = []
            break
        idx = int(length/num_thr)
        thread_points.append(grid_points[:idx])
        grid_points = grid_points[idx:]

    print(length, [len(_) for _ in thread_points])
    threads = []
    for idx, i in enumerate(thread_points):
        t = Thr(i, idx, term1, term2)
        threads.append(t)
        t.start()

    solutions = []
    rounded_solutions = []
    for t in threads:
        thr_solutions = t.join()
        for i in thr_solutions:
            r = round_solution(i)
            if r not in rounded_solutions:
                rounded_solutions.append(r)
                solutions.append(round_solution(i, ACCURACY, Term(term1) - Term(term2)))
    
    return solutions

def round_solution(solution, round_accuracy=ACCURACY - 2, term=None):
    keys = list(solution.keys())
    rounded = Solution()
    if term:
        rounded.term = term
    for k in keys:
        rounded[k] = round(solution[k], round_accuracy)
    return rounded
