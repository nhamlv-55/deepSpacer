import metaspacer as ms

chc = ms.load('/home/nle/workspace/deepSpacer/chc-lia-0006.smt2', type = "smt2")
q = ms.Query(chc = chc, text = "( and (= itp_0_n 0) (> itp_1_n 1) )")
print(q.solve())
q.update_query("(= itp_2_n 3)")
print(q.solve())

