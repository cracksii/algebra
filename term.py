from math import pi, sin, cos, tan, asin, acos, atan

class Term:
    def __init__(self, start=None):
        if isinstance(start, Term):
            self.instructions = start.instructions
            self.variables = start.variables
            return

        from variable import Variable
        self.variables = []
        self.instructions = []
        if not start:
            return

        if isinstance(start, int) or isinstance(start, float) or isinstance(start, Variable):
            start = ("add", start)
            if isinstance(start[1], Variable):
                self.variables = [start[1]]
        elif isinstance(start[1], Variable):
            self.variables = [start[1]]
        else:
            raise ValueError("Cannot initialize Term from ", type(start))
        self.instructions = [start]

    def __add__(self, o):
        return self.operation(('add', o))

    def __sub__(self, o):
        return self.operation(('add', -o))

    def __mul__(self, o):
        return self.operation(('mul', o))

    def __pow__(self, o):
        return self.operation(('pow', o))
    
    def __truediv__(self, o):
        return self.operation(('div', o))
    
    def __rtruediv__(self, o):
        return self.operation(('rdiv', o))

    def __rpow__(self, o):
        return self.operation(('rpow', o))

    def __rsub__(self, o):
        return self.operation(('rsub', o))
    
    def __neg__(self):
        return self.__mul__(-1)
        
    __radd__ = __add__
    __rmul__ = __mul__

    def __eq__(self, o):
        from solver import solve

        if isinstance(o, float) or isinstance(o, int) or self.variables == o.variables and len(self.variables) == 1:
            return solve(self, o)
        raise ValueError("__eq__ solving only works for single variable terms!")

    def __repr__(self):
        from variable import Variable
        output = ""

        operations = {
            "add": "+",
            "mul": "*",
            "pow": "^",
            "div": "/"
        }
        output = ""

        for idx, instr in enumerate(self.instructions):
            op, val = instr

            if op in operations.keys():
                op = operations[op]
            # print(instr)
            if idx == 0:
                if isinstance(val, Variable):
                   # output += f"{'(' * (len(self.instructions) - 1)}{val.selfname()}"
                    output += val.selfname()
                else:
                    output += str(val)
            else:
                if isinstance(val, Variable):
                    output += f" {op} {val.selfname()})"
                elif isinstance(val, Term):
                    output += f" {op} ({str(val).strip().replace("|", "")}"
                else:
                    output += f" {op} {val})"

        return f"|{output}|"

    def operation(self, k):
        from variable import Variable
        op, val = k
        self.instructions.append((op, val))

        if isinstance(val, Variable):
            self.variables.append(val)
        elif isinstance(val, Term):
            self.variables.extend([_ for _ in val.variables if _ not in self.variables])
        return self

    def compute(self, vals):
        from variable import Variable
        assert isinstance(vals, dict) or ((isinstance(vals, float) or isinstance(vals, int)) and len(self.variables) == 1)
        if isinstance(vals, dict):
            for k in [_ for _ in self.variables if _ not in vals.keys()]:
                vals[k] = 1
        else:
            vals = {self.variables[0]: vals}
        value = 0

        for op, val in self.instructions:
            if isinstance(val, Term):
                val = val.compute(vals)
            elif isinstance(val, Variable):
                val = vals[val]

            if op == 'add':
                value += val
            elif op == 'mul':
                value *= val
            elif op == 'pow':
                value **= val
            elif op == 'rpow':
                value = val ** value
            elif op == 'div':
                if val == 0:
                    return float('nan')
                value /= val
            elif op == 'rdiv':
                if value == 0:
                    return float('nan')
                value = val / value
            elif op == 'rsub':
                value = val - value
            elif op == 'rsin':
                value = sin(value * pi / 180)
            elif op == 'rcos':
                value = cos(value * pi / 180)
            elif op == 'rtan':
                value = tan(value * pi / 180)
            elif op == 'rasin':
                value = asin(value * pi / 180)
            elif op == 'racos':
                value = acos(value * pi / 180)
            elif op == 'ratan':
                value = atan(value * pi / 180)

        return value

    def clone(self):
        t = Term()
        for i in self.instructions:
            t.instructions.append(i)
        for i in self.variables:
            t.variables.append(i)
        return t
    
