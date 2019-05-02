import metaspacer as ms

chc = ms.load('/home/nle/workspace/deepSpacer/chc-lia-0006.smt2', type = "smt2")
chc.dump()
q = ms.Query(chc = chc)
#res, _ = q.execute(chc.queries[0], params = {"spacer.max_level": 1})
#print(q.fp.get_cover_delta(5, chc.queries[0]))
#print(q.fp.get_num_levels(chc.predicates[0]))
#print(res)
res, _ = q.execute("(itp ( itp_0_n , itp_1_n , itp_2_n , itp_3_n ) )", params = {"spacer.max_level": 5})
print("res", res)
print("get_answer",_.get_answer())
print("get_ground_sat", _.get_ground_sat_answer())
print("************")
res, f = q.execute("(= itp_3_n 1)")
print(res)
print(f.get_ground_sat_answer())

