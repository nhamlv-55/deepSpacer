from flask import Flask, send_from_directory, jsonify, request
import json
from z3 import *
open_log('/tmp/z3log')
import metaspacer as ms

app = Flask(__name__)

@app.route("/home/")
def home():

    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def send_json(path):
    return send_from_directory('static', path)



@app.route("/execute_file/", methods = ["POST"])
def execute_file():
    print(request.form)
    filename = request.form["filename"]
    query = request.form["query_text"]
    params = json.loads(request.form["params"])
    time = "Now"
    params["spacer.print_json"] = "static/"+filename + "." + time + ".json"
    chc = ms.load('../../benchmarks/chc-comp18-benchmarks/lia/'+filename, type='smt2')
    q = ms.Query(chc)
    if query=="":
        query = chc.queries[0]
    res, _ = q.execute(query, params = params)
    return jsonify(result = str(res), json_filename = params["spacer.print_json"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug = True, port=8888)
