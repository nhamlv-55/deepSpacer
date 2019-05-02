from z3 import *
class Query():
    def __init__(self, chc = None ):
        self.chc = chc
        self.fp = None
        self.text = None
        self.sorts = {}
        self.decls = {}
        self.vs = []

    def __del__(self):
        del self.fp
        

    def declare_undefined_vars(self, _vars):
        for v in _vars:
            predicate, idx, _ = v.split("_")
            self.sorts[v] = self.chc.all_var_sort[predicate][int(idx)]
            new_decl = Const(v, self.sorts[v])
            self.decls[v] = new_decl.decl()
            self.vs.append(new_decl)



    def _from_str(self, text):
        tokens = text.split()
        _vars = set()
        for token in tokens:
            if "_n" in token:
                _vars.add(token)
        self.declare_undefined_vars(_vars)
        u = parse_smt2_string("(assert %s)"%text, self.sorts, self.decls)
        self.text = text
        vs = []
        for v in self.vs:
            if v.decl().name() in _vars:
                vs.append(v)
        self.query = Exists(vs, u[0])


    def create_fp(self):
        fp = Fixedpoint()
        for p in self.chc.predicates:
            print("adding predicates", p)
            fp.register_relation(p)
        for r in self.chc.rules:
            print("adding rule", r)
            fp.add_rule(r)
        self.fp = fp

    def set_params(self, params, z3_params):
        for k in params:
            self.fp.set(k, params[k])
            
        for k in z3_params:
            set_param(k, z3_params[k])

    def solve(self, params, z3_params):
        if self.fp!=None:
            self.set_params(params, z3_params)
            return self.fp.query(self.query)
        
        else:
            self.create_fp()
            self.set_params(params, z3_params)
            return self.fp.query(self.query)

    def execute(self, query, params = {}, z3_params = {}):
        if isinstance(query, str):
            self._from_str(query)
        else:
            self.query = query
        result = self.solve(params, z3_params)
        return result, self.fp


    def dump(self):
        print(self.fp)
        print(self.query)
        print(self.text)

if __name__ == "__main__":
    from .chc_problem import CHCProblem
    chc = CHCProblem()
    chc.load('/home/nle/workspace/deepSpacer/chc-lia-0006.smt2')
    chc.dump()
    q = Query(chc = chc, text = "( and (= itp_0_n 0) (> itp_1_n 1) )")
    q.dump()
    print(q.solve())
