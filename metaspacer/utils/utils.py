import z3
from ..core import CHCProblem 
def load(filename, type = None):
    fp = z3.Fixedpoint()
    if type =="datalog":
        queries = fp.parse_file(filename)

    elif type == "smt2":
        queries = 

