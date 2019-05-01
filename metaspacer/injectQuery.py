from z3 import *
class Str2QueryConverter:
    def __init__(self, fs = None):
        self.defined_vars = set()
        self.all_var_sort = {}
        self.sorts = {}
        self.decls = {}
        self.vs = []
        if fp:
            self.get_all_vs(fs)

    def get_all_vs(self, fs):
        for f in fs:
            name = f.body().arg(1).decl()
            self.all_var_sort[str(f.body().arg(1).decl())] = self.get_var_sort(f)

    def get_var_sort(self, f):
        var_sort = []
        for i in range(f.num_vars()):
            var_sort.append(f.var_sort(i))
        return tuple(var_sort)

    def get_all_vars(self, s):
        tokens = s.split()
        results = set()
        for token in tokens:
            if "_n" in token:
                results.add(token)
        return results

    def declare_undefined_vars(self, all_vars):
        for v in all_vars:
            predicate, idx, _ = v.split("_")
            if v not in self.defined_vars:
                self.defined_vars.add(v)
                self.sorts[v] = self.all_var_sort[predicate][int(idx)]
                new_decl = Const(v, self.sorts[v])
                self.decls[v] = new_decl.decl()
                self.vs.append(new_decl)

    def string_to_query(self, s):
        all_vars = self.get_all_vars(s)
        self.declare_undefined_vars(all_vars)
        u = parse_smt2_string("(assert %s)"%s, self.sorts, self.decls)[0]
        instance_vs = []
        for v in self.vs:
            if str(v.decl()) in all_vars:
                instance_vs.append(v)
        return Exists(instance_vs, u)

if __name__ == '__main__':
    fs = parse_smt2_file('chc-lia-0006.smt2')
    fp = Fixedpoint()
    init = fs[0]

    converter = Str2QueryConverter(fs)
    q1 = converter.string_to_query('( and (= itp_0_n 0) (> itp_1_n 1) )')
    print(q1)
    q2 = converter.string_to_query('(= itp_1_n 5)')
    print(q2)
    q3 = converter.string_to_query('(and (= itp_0_n 0) (= itp_7_n 12))')
    print(q3)
