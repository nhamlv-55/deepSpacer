from z3 import *
class Query():
    def __init__(self, chc ):
        self.chc = chc
        self.text = None
        self.sorts = {}
        self.decls = {}
        self.vs = []

        self.fp = self.create_fp()

    def __del__(self):
        del self.fp

    def _declare_undefined_vars(self, _vars):
        for v in _vars:
            predicate, idx, _ = v.split("_")
            self.sorts[v] = self.chc.all_var_sort[predicate][int(idx)]
            new_decl = Const(v, self.sorts[v])
            self.decls[v] = new_decl.decl()
            self.vs.append(new_decl)
        print(self.decls)
        print(self.vs)


    def _from_str(self, text):
        tokens = tokenize(text)
        print("tokens:", tokens)
        _vars = set()
        _preds = set()
        for token in tokens:
            if "_n" in token:
                _vars.add(token)
                
        self._declare_undefined_vars(_vars)
        print("(assert %s)"%text, self.sorts, self.decls)
        u = parse_smt2_string("(assert %s)"%text, self.sorts, self.decls)
        self.text = text
        vs = set()
        for v in self.vs:
            if v.decl().name() in _vars:
                vs.add(v)
        self.query = Exists(list(vs), u[0])
        print("query:", self.query)
        return self.query

    def get_cover_delta(self, level, predicate):
        return self.fp.get_cover_delta(level, predicate)

    def create_fp(self):
        fp = Fixedpoint()
        for pred_name in self.chc.predicates:
            fp.register_relation(self.chc.predicates[pred_name])
            self.decls[pred_name] = self.chc.predicates[pred_name]
        for r in self.chc.rules:
            fp.add_rule(r)
        self.fp = fp

    def set_params(self, params, z3_params):
        for k in params:
            self.fp.set(k, params[k])
            
        for k in z3_params:
            set_param(k, z3_params[k])

    def solve(self, level, params, z3_params):
        if self.fp==None:
            self.create_fp()
        self.set_params(params, z3_params)

        if level>0:
            print("call query_from_lvl from Query")
            return self.fp.query_from_lvl(level, self.query)
        else:
            print("call query from Query")
            return self.fp.query(self.query)

    def execute(self, query, level = -1, params = {}, z3_params = {}):
        print("call Query.execute")
        self.query = None
        if isinstance(query, str):
            self._from_str(query)
        else:
            self.query = query
        if self.query!=None:
            result = self.solve(level, params, z3_params)
            print("fp:\n\t", self.fp)
            return result, self.fp
        else:
            return "error", self.fp


    def dump(self):
        print(self.fp)
        print(self.query)
        print(self.text)

def tokenize(chars):
    #Convert a string of characters into a list of tokens.
    #Snippet from Peter Norvig's (How to Write a (Lisp) Interpreter (in Python))
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

if __name__ == "__main__":
    from .chc_problem import CHCProblem
    chc = CHCProblem()
    chc.load('/home/nle/workspace/deepSpacer/chc-lia-0115.smt2')
    chc.dump()
    
    q = Query(chc.queries[0])
    q.dump()
    print(q.solve())
