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

    def _declare_vars(self, _preds):
        for pred_name in _preds:
            num_vars = self.chc.predicates[pred_name].arity()
            for idx in range(num_vars):
                var_name = pred_name+"_"+str(idx)+"_n"
                self.sorts[var_name] = self.chc.all_var_sort[pred_name][idx]
                new_decl = Const(var_name, self.sorts[var_name])
                self.decls[var_name] = new_decl.decl()
                self.vs.append(new_decl)
        print(self.decls)
        print(self.vs)

    def _append_predicate(self, text, _preds):
        """
        auto append all related predicates to the query string
        e.g: itp is (itp Int Int Int Int)
        (<= itp_0_n 8) ==> (and (itp itp_0_n itp_1_n itp_2_n itp_3_n)
                                (<= itp_0_n 8)
                           )
        """
        result = "(and "
        for pred_name in _preds:
            pred_string = "("+pred_name
            print(dir(self.chc.predicates[pred_name]))
            num_vars = self.chc.predicates[pred_name].arity()
            for i in range(num_vars):
                pred_string = pred_string + " " + pred_name + "_" + str(i)+  "_n" 
            result += pred_string+")\n"
        result += text + ")"
        
        return result


    def _from_str(self, text):
        tokens = tokenize(text)
        print("tokens:", tokens)
        _preds = set()
        for token in tokens:
            if "_n" in token:
                pred_name, idx, _ = token.split("_")
                _preds.add(pred_name)
        self._declare_vars(_preds)
        text = self._append_predicate(text, _preds)
        print("(assert %s)"%text, self.sorts, self.decls)
        u = parse_smt2_string("(assert %s)"%text, self.sorts, self.decls)
        self.text = text
        vs = set()
        for v in self.vs:
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
