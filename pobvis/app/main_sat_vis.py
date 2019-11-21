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



def startSpacer(iterative):
    request_params = request.get_json()
    fileContent = request_params.get('file', '')
    print(request_params)

    spacerUserOptions = request_params.get("spacerUserOptions", "")

    temporaryFile = open("input_file.smt2", "wb")
    temporaryFile.write(str.encode(fileContent))
    temporaryFile.flush() # commit file buffer to disk so that Spacer can access it

    if iterative:
        status= spacerWrapper.startIterative(temporaryFile.name, spacerUserOptions)
        return json.dumps({'status': status, 'spacerState': "running", 'nodes_list': {}})
    else:
        progress_trace = spacerWrapper.start(temporaryFile.name, spacerUserOptions)

        lines = ms.parse(progress_trace)
        temporaryFile.close()
        print("close tempfile")
        return json.dumps({'status': "success", 'spacerState': "saturation", 'nodes_list': lines})

def poke():

    with open("spacer.log", "r") as f:
        progress_trace = f.readlines()

    with open("verbose", "r") as f:
        verbose = f.readlines()

    with open("stat", "r") as f:
        stats = f.readlines()
        #check if there are no error in running
        if len(verbose)>0 and verbose[0].startswith('ERROR'):
            spacerState = 'stopped. '
            spacerState += verbose[0]
            return json.dumps({'status': "success", 'spacerState': spacerState, 'nodes_list': {}})
        elif len(stats)>0:
            if 'sat' in stats[0] or 'bounded' in stats[0] or 'unknown' in stats[0]:
                spacerState = 'finished'
                spacerState += '. Result: %s'%stats[0]
                print(spacerState)
            else:
                spacerState = 'Unknown returned message'
        else:
            spacerState = 'running'
    
    lines = ms.parse(progress_trace)

    return json.dumps({'status': "success", 'spacerState': spacerState, 'nodes_list': lines})


@app.route('/spacer/start', methods=['POST'])
def handle_startSpacer():  
    return startSpacer(False)

@app.route('/spacer/startiterative', methods=['POST'])
def handle_startSpacerIterative():
    return startSpacer(True)
@app.route('/spacer/poke', methods=['POST'])
def handle_poke():
    return poke()
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
