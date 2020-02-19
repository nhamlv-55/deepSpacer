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
import pysmt.operators as pyopt
import os
import sqlite3
from flask import g
from settings import DATABASE, MEDIA, options_for_visualization
import metaspacer as ms
from subprocess import PIPE, STDOUT, Popen, run
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)
from datetime import datetime

parser = argparse.ArgumentParser(description='Run Spacer Server')
parser.add_argument("-z3", "--z3", required=True, action="store", dest="z3Path", help="path to z3 python")
args = parser.parse_args()
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
def insert_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    get_db().commit()
    cur.close()

def fetch_exps():
    exps_list = []
    for exp in query_db('select * from exp'):
        r = {}
        for k in exp.keys():
            r[k] = exp[k]
        exps_list.append(r)
    return json.dumps({'status': "success", 'exps_list':exps_list})

def get_new_exp_name(exp_name):
    now = datetime.now()
    current_time = now.strftime("%d%m%y_%H_%M_%S")
    return exp_name+"_"+current_time

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

    Popen(run_args, stdin=PIPE, stdout=stdout_file, stderr=stderr_file, cwd = exp_folder, close_fds = True)

    return json.dumps({'status': "success", 'spacerState': "running", 'nodes_list': {}})

def poke():
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




    # with open("stat", "r") as f:
    #     stats = f.readlines()
    #     #check if there are no error in running
    #     if len(verbose)>0 and verbose[0].startswith('ERROR'):
    #         spacerState = 'stopped. '
    #         spacerState += verbose[0]
    #         return json.dumps({'status': "success", 'spacerState': spacerState, 'nodes_list': {}})
    #     elif len(stats)>0:
    #         if 'sat' in stats[0] or 'bounded' in stats[0] or 'unknown' in stats[0]:
    #             spacerState = 'finished'
    #             spacerState += '. Result: %s'%stats[0]
    #             print(spacerState)
    #         else:
    #             spacerState = 'Unknown returned message'
    #     else:
    #         spacerState = 'running'

    #only read spacer.log when there are no errors
    if spacerState == 'running' :
            nodes_list = ms.parse(spacer_log)
            #parse expr to json
            for idx in nodes_list:
                node = nodes_list[idx]
                if node["exprID"]>2:
                    expr = node["expr"]
                    expr_stream = io.StringIO(expr)
                    try:
                        ast = spacerWrapper.rels[0].pysmt_parse_lemma(expr_stream)
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
# @app.route('/spacer/replay', methods=['POST'])
# def handle_replay():
#     return replay()
if __name__ == '__main__':
    app.run()
