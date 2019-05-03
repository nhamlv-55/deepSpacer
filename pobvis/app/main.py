from flask import Flask, send_from_directory, jsonify
from z3 import *
open_log('/tmp/z3log')
import metaspacer as ms

app = Flask(__name__)

@app.route("/home/")
def home():
    return send_from_directory('static', 'index.html')






chc = ms.load('chc-lia-0006.smt2', type='smt2')
q = ms.Query(chc)
q.execute(q.chc.queries[0],
         params={'spacer.max_level': 4,
                 'xform.slice': False,
                 'xform.inline_eager': False,
                 'xform.inline_linear': False,
                 })

p = chc.predicates[0].decl()
for i in range(0, q.fp.get_num_levels(p)):
   print('Lemmas at level', i, 'of', p)
   print(q.fp.get_cover_delta(i, p))
print('Lemmas at oo of', p)
print(q.fp.get_cover_delta(-1, p))
