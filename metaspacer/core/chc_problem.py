from z3 import *
class CHCProblem():
    def __init__(self, filename = None):
        self.filename = filename
        self.variables = set()
        self.rules = []
        self.predicates = []
        self.all_var_sort = {}
        self.queries = []
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
            predicate = f.body().arg(1)
            self.predicates.append(predicate)
            # add variables and sorts
            self.all_var_sort[predicate.decl().name()] = self.get_var_sort(f)
            # add queries. Queries are predicate with no argument
            if predicate.num_args()==0:
                self.queries.append(predicate)
            # add rule
            self.rules.append(f)
        print("=======DONE LOADING =======")

    def dump(self):
        print("filename:", self.filename)
        print("variables:", self.variables)
        print("rules:", self.rules)
        print("predicates", self.predicates)
        print("queries:", self.queries)
        print("all_var_sort", self.all_var_sort)

if __name__ == "__main__":
    chc = CHCProblem()
    chc.load('/home/nle/workspace/deepSpacer/chc-lia-0006.smt2')
    chc.dump()
    
