"""The application entry point."""

import sys
if sys.version_info.major < 3:
    raise Exception("User error: This application only supports Python 3, so please use python3 instead of python!")
import json
from flask import Flask, request
from flask_cors import CORS
import tempfile
import argparse
from chctools import horndb as H
import io
import os
from settings import DATABASE, MEDIA, options_for_visualization
import metaspacer as ms
from subprocess import PIPE, STDOUT, Popen, run
from chctools import horndb as H
from utils import *
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)

parser = argparse.ArgumentParser(description='Run Spacer Server')
parser.add_argument("-z3", "--z3", required=True, action="store", dest="z3Path", help="path to z3 python")
args = parser.parse_args()
def startSpacer():
    request_params = request.get_json()
    fileContent = request_params.get('file', '')
    exp_name = request_params.get('name', '')
    new_exp_name = get_new_exp_name(exp_name)
    print(new_exp_name)
    insert_db('INSERT INTO exp(name, done, result, aux, time) VALUES (?,?,?,?,?)',(new_exp_name, 0, "UNK", "NA", 0))


    spacerUserOptions = request_params.get("spacerUserOptions", "")

    exp_folder = os.path.join(MEDIA, new_exp_name)
    os.mkdir(exp_folder)

    input_file = open(os.path.join(exp_folder, "input_file.smt2"), "wb")
    input_file.write(str.encode(fileContent))
    input_file.flush() # commit file buffer to disk so that Spacer can access it

    stderr_file = open(os.path.join(exp_folder, "stderr"), "w")
    stdout_file = open(os.path.join(exp_folder, "stdout"), "w")

    run_args = [args.z3Path]
    run_args.extend(spacerUserOptions.split())
    run_args.extend(options_for_visualization)
    run_args.append('input_file.smt2')
    print(run_args)

    with open(os.path.join(exp_folder, "run_cmd"), "w") as f:
        run_cmd = " ".join(run_args)
        f.write(run_cmd)

    Popen(run_args, stdin=PIPE, stdout=stdout_file, stderr=stderr_file, cwd = exp_folder)

    return json.dumps({'status': "success", 'spacerState': "running", 'nodes_list': {}, 'exp_name': new_exp_name})

def poke():
    #TODO: finish parsing using all the files in the exp_folder (input_file, etc.)
    request_params = request.get_json()
    exp_path = request_params.get('exp_path', '')
    exp_folder = os.path.join(MEDIA, exp_path)
    nodes_list = []
    spacerState = "running"
    with open(os.path.join(exp_folder, "stdout"), "r") as f:
        stdout = f.readlines()
    with open(os.path.join(exp_folder, "stderr"), "r") as f:
        stderr = f.readlines()
    with open(os.path.join(exp_folder, ".z3-trace"), "r") as f:
        z3_trace = f.readlines()
    with open(os.path.join(exp_folder, "spacer.log"), "r") as f:
        spacer_log = f.readlines()

    #load the file into db for parsing 
    db = H.load_horn_db_from_file(os.path.join(exp_folder, "input_file.smt2"))
    rels = []
    for rel_name in db._rels:
        rel = db.get_rel(rel_name)
        rels.append(rel)

    #TODO: only read spacer.log when there are no errors
    if spacerState == 'running' :
        nodes_list = ms.parse(spacer_log)
        #parse expr to json
        for idx in nodes_list:
            node = nodes_list[idx]
            if node["exprID"]>2:
                expr = node["expr"]
                expr_stream = io.StringIO(expr)
                try:
                    ast = rels[0].pysmt_parse_lemma(expr_stream)
                    ast_json = order_node(to_json(ast))
                    node["ast_json"] = ast_json

                except Exception as e:
                    print("Exception when ordering the node:", e)
                    print("Broken Node", node)
                    print("Broken Node exprID:", node["exprID"])
                    node["ast_json"] = {"type": "ERROR", "content": "trace is incomplete"}


    return json.dumps({'status': "success", 'spacerState': spacerState, 'nodes_list': nodes_list})


@app.route('/spacer/fetch_exps', methods=['POST'])
def handle_fetch_exps():
    return fetch_exps()
@app.route('/spacer/startiterative', methods=['POST'])
def handle_startSpacerIterative():
    return startSpacer()
@app.route('/spacer/poke', methods=['POST'])
def handle_poke():
    return poke()
if __name__ == '__main__':
    app.run()
