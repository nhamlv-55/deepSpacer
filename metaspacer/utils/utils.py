import z3

def lemma_to_string(lemma, pred):
    """
    convert a lemma returned by get_cover_delta into a string that parse_smt2_string can parse
    """
    const_list = [z3.Const(pred.name()+"_"+str(j), pred.domain(j)) for j in range(pred.arity())]
    lhs = pred(*const_list)
    rhs = z3.substitute_vars(lemma, *(const_list))
    imp = z3.Implies(lhs, rhs)
    forall = z3.ForAll(list(const_list), imp)
    lemma_str = "(assert %s)"%forall.sexpr()
    return lemma_str

def stripQuantifierBlock (expr) :
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
    consts = list ()
    # outside-in order of variables; z3 numbers variables inside-out but
    # substitutes outside-in
    for i in reversed (range (expr.num_vars ())) :
        v_name = expr.var_name (i)
        v_sort = expr.var_sort (i)
        consts.append (z3.Const (v_name, v_sort))
    matrix = z3.substitute_vars (expr.body (), *consts)
    return (consts, matrix)


