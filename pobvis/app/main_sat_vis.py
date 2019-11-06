"""The application entry point."""

import sys
if sys.version_info.major < 3:
    raise Exception("User error: This application only supports Python 3, so please use python3 instead of python!")

import json

from flask import Flask, request
from flask_cors import CORS
import metaspacer as ms
#from model.parsing import parse
#from model.spacer import SpacerWrapper

import tempfile

import argparse
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)

parser = argparse.ArgumentParser(description='Run Spacer Server')
parser.add_argument("-z3", "--z3", required=True, action="store", dest="z3Path", help="path to z3 python")
args = parser.parse_args()
spacerWrapper = ms.SpacerWrapper(args.z3Path)

def startSpacer(manualCS):
    request_params = request.get_json()
    fileContent = request_params.get('file', '')
    print(request_params)

    spacerUserOptions = request_params.get("spacerUserOptions", "")

    temporaryFile = tempfile.NamedTemporaryFile()
    temporaryFile.write(str.encode(fileContent))
    temporaryFile.flush() # commit file buffer to disk so that Spacer can access it

    if manualCS:
        output = spacerWrapper.startManualCS(temporaryFile.name, spacerUserOptions)
    else:
        output, graph_json, progress_trace = spacerWrapper.start(temporaryFile.name, spacerUserOptions)

    print(output)
    lines = ms.parse(progress_trace)
    temporaryFile.close()

    # filename = request.form["filename"]
    # print(folder + filename)
    # query = request.form["query_text"]
    # show_formula = request.form["show_formula"]
    # params = json.loads(request.form["params"])
    # level = int(request.form["level"])
    # interactive = request.form["interactive"]
    # lemmas_file = request.form["lemmas_file"]
    # time = "Now"
    # params["spacer.print_json"] = "static/"+filename + "." + time + ".json"
    return json.dumps({'status': "success", 'spacerState': "saturation", 'nodes_list': lines})


# def startSpacer(manualCS):
#     request_params = request.get_json()
#     fileContent = request_params.get('file', '')
#     print(request_params)
#     return
#     if fileContent == "":
#         message = "User error: Input encoding must not be empty!"
#         print(message)
#         return json.dumps({
#             "status" : "error",
#             "message" : message
#         })
#     spacerUserOptions = request_params.get("spacerUserOptions", "")

#     temporaryFile = tempfile.NamedTemporaryFile()
#     temporaryFile.write(str.encode(fileContent))
#     temporaryFile.flush() # commit file buffer to disk so that Spacer can access it

#     if manualCS:
#         output = spacerWrapper.startManualCS(temporaryFile.name, spacerUserOptions)
#     else:
#         output = spacerWrapper.start(temporaryFile.name, spacerUserOptions)

#     if spacerWrapper.spacerState == "error":
#         message = "User error: Wrong options for Spacer or mistake in encoding"
#         print(message)
#         return json.dumps({
#             "status" : "error",
#             "message" : message
#         })

#     lines = parse(output)
#     temporaryFile.close()

#     if manualCS:
#         return json.dumps({
#             'status' : "success",
#             'spacerState' : spacerWrapper.spacerState, 
#             'lines' : [line.to_json() for line in lines], 
#         })
#     else:
#         return json.dumps({
#             'status' : "success",
#             'spacerState' : spacerWrapper.spacerState, 
#             'lines' : [line.to_json() for line in lines]
#         })

@app.route('/spacer/start', methods=['POST'])
def handle_startSpacer():  
    return startSpacer(False)

@app.route('/spacer/startmanualcs', methods=['POST'])
def handle_startSpacerManualCS():
    return startSpacer(True)

@app.route('/spacer/select', methods=['POST'])
def handle_selection():    
    request_params = request.get_json()
    selectedId = int(request_params.get('id', ''))

    if(spacerWrapper.spacerState != "running"):
        message = "User error: Spacer is not running, so it makes no sense to perform selection!"
        print(message)
        return json.dumps({
            'status' : "error",
            "message" : message,
            'spacerState' : spacerWrapper.spacerState
        })
    # TODO: check that selectedId was accepted by Spacer
    output = spacerWrapper.select(selectedId)
    lines = parse(output)

    return json.dumps({
        "status" : "success",
        'spacerState' : spacerWrapper.spacerState, 
        'lines' : [line.to_json() for line in lines], 
    })  

if __name__ == '__main__':
    app.run()
