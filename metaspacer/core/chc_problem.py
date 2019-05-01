from z3 import *
class CHCProblem():
    def __init__(self, filename = None):
        self.filename = filename
        self.variables = set()
        self.rules = []
        self.predicates = set()
        self.all_var_sort = {}
        if filename != None:
            self.load(filename)
    def get_var_sort(self, f):
        """
        Given an expression, return a tuple of all sort
        """
        var_sort = []
        for i in range(f.num_vars()):
            var_sort.append(f.var_sort(i))
        return tuple(var_sort)
    
    def load(self, filename):
        self.filename = filename
        fs = parse_smt2_file(filename)
        for f in fs:
            print(f)
            # add predicates
            predicate = f.body().arg(1).decl()
            self.predicates.add(predicate)
            # add variables and sorts
            self.all_var_sort[predicate.name()] = self.get_var_sort(f)

        self.rules.extend(fs)


    def dump(self):
        print(self.filename)
        print(self.variables)
        print(self.rules)
        print(self.predicates)
        print(self.all_var_sort)

if __name__ == "__main__":
    chc = CHCProblem()
    chc.load('/home/nle/workspace/deepSpacer/chc-lia-0006.smt2')
    chc.dump()
         
