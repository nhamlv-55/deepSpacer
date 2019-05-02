import metaspacer as ms

chc = ms.load('/home/nle/workspace/deepSpacer/chc-lia-0006.smt2', type = "smt2")
q = ms.Query(chc = chc)
print(chc.queries)
res, _ = q.execute(chc.queries[0], params = {"spacer.max_level": 20})
print(res)
res, _ = q.execute("( and (= itp_0_n -5) (> itp_0_n 1) )", params = {"spacer.max_level": 5})
print("res", res)
print("get_answer",_.get_answer())
print("************")
print(res)
print(q.query)
res, f = q.execute("(= itp_3_n 1)")
print(res)
print(f.get_ground_sat_answer())

