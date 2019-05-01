import z3
from ..core import CHCProblem 
def load(filename, type = None):
    chc = CHCProblem()
    if type=="smt2":
        chc.load(filename)
    return chc
#    fp = z3.Fixedpoint()
#    c = CHCProblem()
#    if type =="datalog":
#        queries = fp.parse_file(filename)
#
#    elif type == "smt2":
#        queries = 

