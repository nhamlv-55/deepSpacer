"""The application entry point."""

import sys
if sys.version_info.major < 3:
    raise Exception("User error: This application only supports Python 3, so please use python3 instead of python!")

import json

from flask import Flask, request
from flask_cors import CORS
import metaspacer as ms
import tempfile
import argparse
from chctools import horndb as H
import io
import pysmt.operators as pyopt

import sqlite3
from flask import g
from settings import DATABASE

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

def get_new_exp_name():
    now = datetime. now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

# ERROR_OBJ = {"type": "ERROR", "content": "trace is incomplete"}
# def calculate_val(node):
#     if node.is_real_constant():
#         frac = node._content.payload
#         val = frac.numerator / frac.denominator
#         return round(val, 4)
#     return str(node._content.payload[0])
# def to_json(node, debug = False):
#     if debug: print(node, node.get_type(), node.args())
#     if node.is_real_constant():
#         type_str = "0_REAL_CONSTANT" #hack to put real constant at the end
#     else:

#         type_str = pyopt.op_to_str(node.node_type())
#         if debug:
#             print("NODE TYPE:", node.node_type())
#             print("TYPE_STR:", type_str)
#     if len(node.args())==0:
#         obj = {"type": type_str, "content":calculate_val(node)}
#         return obj
#     else:
#         args = []
#         for a in node.args():
#             args.append(to_json(a, debug))
#         obj = {"type": type_str, "content": args}
#         return obj
    
    
# def order_node(node):
#     args = node["content"]
#     if isinstance(args, list):
#         for idx in range(len(args)):
#             args[idx] = order_node(args[idx])
#         #only order commutative operators
#         if node["type"]=="PLUS" or node["type"]=="TIMES" or node["type"]=="AND":
#             args = sorted(args, key=lambda k: (k["type"], str(k["content"])), reverse = True) 
#         node["content"] = args
#     return node


spacerWrapper = ms.SpacerWrapper(args.z3Path)



def startSpacer():
    new_exp_name = get_new_exp_name()
    print(new_exp_name)
    insert_db('INSERT INTO exp(name, done, result, aux, time) VALUES (?,?,?,?,?)',(new_exp_name, 0, "UNK", "NA", 0))

    request_params = request.get_json()
    fileContent = request_params.get('file', '')

    spacerUserOptions = request_params.get("spacerUserOptions", "")

    temporaryFile = open("input_file.smt2", "wb")
    temporaryFile.write(str.encode(fileContent))
    temporaryFile.flush() # commit file buffer to disk so that Spacer can access it

    # status= spacerWrapper.startIterative(temporaryFile.name, spacerUserOptions)
    return json.dumps({'status': "success", 'spacerState': "running", 'nodes_list': {}})

# def replay():
#     request_params = request.get_json()
#     fileContent = request_params.get('file', '')
#     print(len(fileContent))
#     progress_trace = fileContent.splitlines(keepends=True)

#     nodes_list = ms.parse(progress_trace)
#     #parse expr to json
#     for idx in nodes_list:
#         node = nodes_list[idx]
#         #XXX: FIXME temporary disable reordering because parsing is not really modular.
        
#         node["ast_json"] = {"type": "ERROR", "content": "Don't know how to parse in replay mode yet"}
#         # if node["exprID"]>2:
#         #     expr = node["expr"]
#         #     expr_stream = io.StringIO(expr)
#         #     try:
#         #         ast = spacerWrapper.rels[0].pysmt_parse_lemma(expr_stream)
#         #         ast_json = order_node(to_json(ast))
#         #         node["ast_json"] = ast_json
#         #     except Exception as e:
#         #         node["ast_json"] = {"type": "ERROR", "content": "trace is incomplete"}

#     return json.dumps({'status': "success", 'spacerState': 'replay', 'nodes_list': nodes_list})

# def poke():
#     nodes_list = []
#     spacerState = "UNKNOWN"
#     with open("verbose", "r") as f:
#         verbose = f.readlines()

#     with open("stat", "r") as f:
#         stats = f.readlines()
#         #check if there are no error in running
#         if len(verbose)>0 and verbose[0].startswith('ERROR'):
#             spacerState = 'stopped. '
#             spacerState += verbose[0]
#             return json.dumps({'status': "success", 'spacerState': spacerState, 'nodes_list': {}})
#         elif len(stats)>0:
#             if 'sat' in stats[0] or 'bounded' in stats[0] or 'unknown' in stats[0]:
#                 spacerState = 'finished'
#                 spacerState += '. Result: %s'%stats[0]
#                 print(spacerState)
#             else:
#                 spacerState = 'Unknown returned message'
#         else:
#             spacerState = 'running'

#     #only read spacer.log when there are no errors
#     if spacerState == 'running' or spacerState.startswith('finished'):
#         with open("spacer.log", "r") as f:
#             progress_trace = f.readlines()

#             nodes_list = ms.parse(progress_trace)
#             #parse expr to json
#             for idx in nodes_list:
#                 node = nodes_list[idx]
#                 if node["exprID"]>2:
#                     expr = node["expr"]
#                     expr_stream = io.StringIO(expr)
#                     try:
#                         ast = spacerWrapper.rels[0].pysmt_parse_lemma(expr_stream)
#                         ast_json = order_node(to_json(ast))
#                         node["ast_json"] = ast_json
                        
#                     except Exception as e:
#                         print("Exception when ordering the node:", e)
#                         print("Broken Node", node)
#                         print("Broken Node exprID:", node["exprID"])
#                         node["ast_json"] = {"type": "ERROR", "content": "trace is incomplete"}


#     return json.dumps({'status': "success", 'spacerState': spacerState, 'nodes_list': nodes_list})


@app.route('/spacer/fetch_exps', methods=['POST'])
def handle_fetch_exps():
    return fetch_exps()
@app.route('/spacer/startiterative', methods=['POST'])
def handle_startSpacerIterative():
    return startSpacer()
# @app.route('/spacer/poke', methods=['POST'])
# def handle_poke():
#     return poke()
# @app.route('/spacer/replay', methods=['POST'])
# def handle_replay():
#     return replay()
if __name__ == '__main__':
    app.run()
