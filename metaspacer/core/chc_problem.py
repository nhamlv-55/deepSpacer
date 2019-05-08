import z3
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

    def _stripQuantifierBlock (self, expr) :
        """ strips the outermost quantifier block in a given expression and returns
        the pair (<list of consts replacing free vars>,
        <body with consts substituted for de-bruijn variables>)

        Example:

        assume expr.is_forall ()
        vars, body = strip_quantifier (expr)
        qexpr = z3.ForAll (vars, body)
        assert qexpr.eq (expr)
        """
        if not z3.is_quantifier (expr) : return ([], expr)
        z3ctx = expr.ctx
        consts = list ()
        # outside-in order of variables; z3 numbers variables inside-out but
        # substitutes outside-in
        for i in reversed (range (expr.num_vars ())) :
            v_name = expr.var_name (i)
            v_sort = expr.var_sort (i)
            consts.append (z3.Const (v_name, self._z3_translate (v_sort, z3ctx)))
        matrix = z3.substitute_vars (expr.body (), *consts)
        return (consts, matrix)

    def _z3_translate (self, x, ctx):
        """ A version of z3.AstRef.translate that handles sorts and function declarations correctly"""
        if x.ctx == ctx: return x
        if isinstance (x, z3.BoolSortRef): return z3.BoolSort (ctx)
        if z3.is_arith_sort (x): 
            if x.is_int (): return z3.IntSort (ctx)
            else :
                assert(x.is_real ())
                return z3.RealSort (ctx)
        if isinstance (x, z3.FuncDeclRef):
            sorts = [z3_translate (x.domain (i), ctx) for i in range (decl.arity ())]
            sorts.append (z3_translate (x.range (), ctx))
            return z3.Function (x.name (), *sorts)

        return x.translate (ctx)

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
                vars, body = self._stripQuantifierBlock(f)
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
    
