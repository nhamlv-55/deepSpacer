# coding: utf-8
from z3 import *
f = parse_smt2_file('chc-lia-0006.smt2')
fp = Fixedpoint()
get_ipython().magic(u'pinfo f')
init = f[0]
init.body()
init.body().arg(1)
init.body().arg(1).decl()
fp.register_relation(init.body().arg(1).decl())
fp.add_rule(f[0])
fp.add_rule(f[1])
question = '(and (= itp_0_n 0) (> itp_1_n 1))'
smt2_str = '(assert ' + question + ')'
name = init.body().arg(1).decl().name()
var0  = name + '_0_n'
var1 = name + '_1_n'
x, y = Ints(var0 + ' ' + var1)
u = parse_smt2_string(smt2_str, {},  {'itp_0_n' : x.decl() , 'itp_1_n' : y.decl()})
qf = Exists([x, y], u[0])
fp.query(qf)
#z3.set_param(verbose=1)
#fp.query(qf)
fp.get_ground_sat_answer()
