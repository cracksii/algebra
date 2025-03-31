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
            if not solution:
                continue
            if solution not in self.solutions:
                self.solutions.append(solution)
        #print(f"{self.idx} finished")
    
    def join(self):
        super().join()
        #print(f"{self.idx} joined")
        return self.solutions

def threaded_solutions(term1, term2, start, width=10, lines=400):
    solved = solve_multi(term1, term2, start)

    solutions = [solved]
    grid = []
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
    while True:
        vals = {}
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
    #print(length, solved, term1, term2)
    for i in range(num_thr):
        if i == num_thr - 1:
            thread_points.append(grid_points)
            grid_points = []
            break
        idx = int(length/num_thr)
        thread_points.append(grid_points[:idx])
        grid_points = grid_points[idx:]

    threads = []
    for idx, i in enumerate(thread_points):
        t = Thr(i, idx, term1, term2)
        threads.append(t)
        t.start()

    solutions = []
    for t in threads:
        thr_solutions = t.join()
        for i in thr_solutions:
            if i not in solutions:
                solutions.append(i)
    
    return solutions
