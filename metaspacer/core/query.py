from z3 import *
from metaspacer.utils import *
import json
class Query():
    def __init__(self, chc, lemmas_file = None, params = {}, z3_params = {}):
        self.chc = chc
        self.text = None
        self.sorts = {}
        self.decls = {}
        self.vs = []
        self.lemmas = None

        self.create_fp()
        self.set_params(params, z3_params)
        if lemmas_file is not None:
            self.load_lemmas(lemmas_file)
        self.query = None
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

    def dump_lemmas(self, filename = None):
        results = {}
        for pred_name in self.chc.predicates:
            results[pred_name] = {}
            pred = self.chc.predicates[pred_name]
            for i in range(self.fp.get_num_levels(pred)):
                print('Lemmas at level', i, 'of', pred)
                lemma = self.fp.get_cover_delta(i, pred)
                lemma_str = lemma_to_string(lemma, pred)
                print(lemma_str)
                results[pred_name][str(i)] = lemma_str
            lemma_oo = self.fp.get_cover_delta(-1, pred)
            lemma_oo_string = lemma_to_string(lemma_oo, pred)
            print("Always true:", lemma_oo_string)
            results[pred_name]["-1"] = lemma_oo_string
        if filename is not None:
            with open(filename, "w") as outstream: json.dump(results, outstream, indent = 4, sort_keys = True)
        self.lemmas = results
        return results

    def load_lemmas(self, filename):
        print("loading lemmas from %s into query.fp"%filename)
        with open(filename, "r") as instream: d = json.load(instream)
        self.lemmas = d
        for pred_name in d:
            lemmas = d[pred_name]
            for k in lemmas:
                if k == "-1":
                    print("adding Always true:",)
                else:
                    print("adding lemmas at level%s:"%k,)
                assertion = parse_smt2_string(lemmas[k], {}, {pred_name: self.chc.predicates[pred_name]})[0]
                print(assertion.body().arg(1))
                property = assertion.body().arg(1)
                self.fp.add_cover(int(k), self.chc.predicates[pred_name], property)

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
        return self.query


    def create_fp(self):
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

    def set_params(self, params, z3_params):
        for k in params:
            self.fp.set(k, params[k])
            
        for k in z3_params:
            set_param(k, z3_params[k])

    def solve(self, level):
        if level>0:
            print("call query_from_lvl from Query")
            return self.fp.query_from_lvl(level, self.query)
        else:
            print("call query from Query")
            print("query:", self.query)
            return self.fp.query(self.query)

    def execute(self, query, level = -1):
        print("call Query.execute")
        if isinstance(query, str):
            self._from_str(query)
        else:
            self.query = query
        print(">>>>>>>>>>>>>>>>>>>>>dump internal lemmas before solving")
        self.dump_lemmas()
        if self.query is not None:
            result = self.solve(level)
            print("dump internal lemmas after solving")
            self.dump_lemmas()
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
    from metaspacer.core.chc_problem import *
    chc = CHCProblem('/home/nv3le/workspace/deepSpacer/benchmarks/chc-comp18-benchmarks/lia/chc-lia-0006.smt2')
#    chc.dump()
    
    q = Query(chc)
#    print(q.fp)
    res, _ = q.execute("( or (< itp_0_n 0) (< itp_1_n 0) (< itp_2_n 0) (< itp_3_n 0))")
#    print(res)
    q1_lemmas =  q.dump_lemmas("dump.json")
#    print("q1 lemmas:==================")
#    print(json.dumps(q1_lemmas, indent=4, sort_keys=True))

    q2 = Query(chc, lemmas_file = 'dump.json')
    q2_lemmas = q2.dump_lemmas()

#    q2.fp.set('spacer.max_level', 10)
#    q2.fp.set('spacer.print_json', "../../pobvis/yusuke.json")
#    q2.load_lemmas('../../pobvis/app/Now_yusuke.smt2_0to10.json')
    res = q2.fp.query(chc.queries[0])
   
    print(res)

