import z3
from ..core import CHCProblem 
def load(filename, type = None):
    chc = CHCProblem()
    if type=="smt2":
        chc.load(filename)
    return chc

def lemma_to_string(lemma, pred):
    """
    convert a lemma returned by get_cover_delta into a string that parse_smt2_string can parse
    """
    const_list = [z3.Const(pred.name()+"_"+str(j), pred.domain(j)) for j in range(pred.arity())]
    lhs = pred(*const_list)
    rhs = z3.substitute_vars(lemma, *(const_list))
    imp = z3.Implies(lhs, rhs)
    forall = z3.ForAll(list(reversed(const_list)), imp)
    lemma_str = "(assert %s)"%forall.sexpr()
    return lemma_str


