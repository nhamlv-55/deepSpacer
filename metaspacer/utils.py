import z3

def load(filename, type = None):
    fp = z3.Fixedpoint()
    if type =="datalog":
        queries = fp.parse_file(filename)
    return fp, queries
