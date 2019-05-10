import z3
from metaspacer.utils import *
class CHCProblem():
    def __init__(self, filename = None):
        self.filename = filename
        self.rules = []
        self.predicates = {}
        self.all_var_sort = {}
        self.queries = []
        if filename != None:
            self.load(filename)
        
    def get_var_sort(self, predicate):
        """
        Given an expression, return a tuple of all sort
        """
        var_sort = []
        for i in range(predicate.num_args()):
            var_sort.append(predicate.arg(i).sort())
        return tuple(var_sort)


    def load(self, filename):
        self.filename = filename
        print("im about to parse %s"%filename)
        fs = z3.parse_smt2_file(filename)
        for f in fs:
            # add predicates
            predicate = f.body().arg(1)
            if predicate.decl().name()=='false':
                print("is query")
                print(predicate.sexpr())
                vars, body = stripQuantifierBlock(f)
                query = z3.Exists(vars, f.body().arg(0))
                print("reconstructed query:", query)
                self.queries.append(query)
            else:
                print("f: ", f)
                self.predicates[predicate.decl().name()] = predicate.decl()
                # add variables and sorts
                self.all_var_sort[predicate.decl().name()] = self.get_var_sort(predicate)
                # add rule
                self.rules.append(f)
        print("=======DONE LOADING =======")
        self.dump()

    def dump(self):
        print("filename:", self.filename)
        print("rules:", self.rules)
        print("predicates", self.predicates)
        print("queries:", self.queries)
        print("all_var_sort", self.all_var_sort)

if __name__ == "__main__":
    chc = CHCProblem()
    chc.load('/home/nv3le/workspace/deepSpacer/benchmarks/chc-comp18-benchmarks/lia/chc-lia-0006.smt2')
    chc.dump()
    
