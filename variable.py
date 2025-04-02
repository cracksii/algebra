from term import Term
from gc import get_objects

class Variable:
    variable_dict = {}
    @classmethod
    def init(cls, variables):   # Called to connect variable obects with their names
        fields = [k for k in variables.keys() if not k.startswith("__") and isinstance(variables[k], cls)]
        for field in fields:
            Variable.variable_dict[id(variables[field])] = field

    @classmethod
    def getname(cls, variable):
        if isinstance(variable, cls):
            variable = id(variable)
        return cls.variable_dict[variable]
    
    @classmethod
    def getbyname(cls, name):
        if name in Variable.variable_dict.values():
            vid = list(Variable.variable_dict.keys())[list(Variable.variable_dict.values()).index(name)]
            for obj in get_objects():
                if id(obj) == vid:
                   return obj
        return None

    def selfname(self):
        return self.variable_dict[id(self)]
    
    def operation(self, k):
        return Term(("add", self)).operation(k)

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

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return f"< {self.selfname()} >"
