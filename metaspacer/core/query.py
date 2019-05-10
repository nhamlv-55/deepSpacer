from z3 import *
import json
class Query():
    def __init__(self, chc, lemma_file = None):
        self.chc = chc
        self.text = None
        self.sorts = {}
        self.decls = {}
        self.vs = []

        self.create_fp(lemma_file = lemma_file)

    def __del__(self):
        del self.fp

    def _declare_vars(self, _preds):
        for pred_name in _preds:
            print(pred_name)
            arity = self.chc.predicates[pred_name].arity()
            for idx in range(arity):
                var_name = pred_name+"_"+str(idx)+"_n"
                if var_name not in self.sorts:
                    self.sorts[var_name] = self.chc.all_var_sort[pred_name][idx]
                    new_decl = Const(var_name, self.sorts[var_name])
                    self.decls[var_name] = new_decl.decl()
                    self.vs.append(new_decl)
        print("self.decls:", self.decls)
        print("self.vs:", self.vs)

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
            num_vars = self.chc.predicates[pred_name].arity()
            for i in range(num_vars):
                pred_string = pred_string + " " + pred_name + "_" + str(i)+  "_n" 
            result += pred_string+")\n"
        result += text + ")"
        
        return result


    def _lemma_to_string(self, lemma, pred):
        const_list = [Const(pred.name()+"_"+str(j), pred.domain(j)) for j in range(pred.arity())]
        lhs = pred(*const_list)
        rhs = substitute_vars(lemma, *(const_list))
        imp = Implies(lhs, rhs)
        forall = ForAll(list(reversed(const_list)), imp)
        lemma_str = "(assert %s)"%forall.sexpr()
        return lemma_str

    def dump_lemmas(self, filename):
        results = {}
        for pred_name in self.chc.predicates:
            results[pred_name] = []
            pred = self.chc.predicates[pred_name]
            for i in range(self.fp.get_num_levels(pred)):
                print('Lemmas at level', i, 'of', pred)
                lemma = self.fp.get_cover_delta(i, pred)
                lemma_str = self._lemma_to_string(lemma, pred)
                results[pred_name].append(lemma_str)
            lemma_oo = self.fp.get_cover_delta(-1, pred)
            lemma_oo_string = self._lemma_to_string(lemma_oo, pred)
            results[pred_name].append(lemma_oo_string)
        with open(filename, "w") as outstream: json.dump(results, outstream)
        return results

    def load_lemmas(self, filename):
        print("loading lemmas from %s into query.fp"%filename)
        with open(filename, "r") as instream: d = json.load(instream)
        for pred_name in d:
            lemmas = d[pred_name]
            for i in range(len(lemmas)-1):
                assertion = parse_smt2_string(lemmas[i], {}, {pred_name: self.chc.predicates[pred_name]})[0]
                print("adding:", assertion.body().arg(1))


                property = assertion.body().arg(1)
                self.fp.add_cover(i, self.chc.predicates[pred_name], property)
            assertion_oo = parse_smt2_string(lemmas[-1], {}, {pred_name: self.chc.predicates[pred_name]})
            property_oo = assertion.body().arg(1)
            self.fp.add_cover(-1, self.chc.predicates[pred_name], property_oo)

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
        self.query = Exists(self.vs, u[0])
        print("query:", self.query)
        return self.query


    def create_fp(self, lemma_file):
        print("call create_fp")
        self.fp = Fixedpoint()
        self.fp.set('xform.slice', False,
                    'xform.inline_eager', False,
                    'xform.inline_linear', False)
        for pred_name in self.chc.predicates:
            self.fp.register_relation(self.chc.predicates[pred_name])
            self.decls[pred_name] = self.chc.predicates[pred_name]
        for r in self.chc.rules:
            self.fp.add_rule(r)
        if lemma_file is not None:
            self.load_lemmas(lemma_file)

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
            print("query:", self.query)
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
    from chc_problem import CHCProblem
    chc = CHCProblem()
    chc.load('/home/nv3le/workspace/deepSpacer/benchmarks/chc-comp18-benchmarks/lia/chc-lia-0006.smt2')
    chc.dump()
    
    q = Query(chc)
#    print(q.fp)
    q.execute(chc.queries[0], params ={'spacer.max_level': 10})
    json_lemmas =  q.dump_lemmas("dump.json")

    q2 = Query(chc)
    q2.load_lemmas("dump.json")
    print("q2.1:\n",q2.fp.get_cover_delta(1, chc.predicates['itp']))

    q3 = Query(chc, lemma_file = "dump.json")
    print("q3.2:\n", q3.fp.get_cover_delta(2, chc.predicates['itp']))
