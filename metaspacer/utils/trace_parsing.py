"""A parser for vampire output."""

import logging
import re
from collections import namedtuple
import json
__all__ = 'parse'

LOG = logging.getLogger('VampireParser')
CLAUSE_REGEX = r'(\d+)\. (.*) \[(\D*) ?([\d,]*)\]( \{[a-z]\w*:\d*(?:,[a-z]\w*:\d*)*\})?'
OUTPUT_PATTERN_SATURATION = re.compile(r'^\[SA\] ([a-z ]{3,15}): ' + CLAUSE_REGEX + '$')
OUTPUT_PATTERN_REDUCTIONS = re.compile(r'^     ([a-z ]{5,12}) ' + CLAUSE_REGEX + '$')
OUTPUT_PATTERN_PREPROCESSING = re.compile(r'^' + CLAUSE_REGEX + '$')
OUTPUT_PATTERN_KEYVALUE = re.compile(r'([a-z]\w*):(\d*)')

class ParsedLine (object):
    def __init__(self, lineType, unitId, unitString, inferenceRule, parents, statistics):
        self.lineType = lineType
        self.unitId = unitId
        self.unitString = unitString
        self.inferenceRule = inferenceRule
        self.parents = parents
        self.statistics = statistics

    def to_json(self):
        return {
            'lineType': self.lineType,
            'unitId' : self.unitId,
            'unitString' : self.unitString,
            'inferenceRule' : self.inferenceRule,
            'parents' : self.parents,
            'statistics' : self.statistics
        }

class Node (object):
    def __init__(self, nodeId, parents, timestamp, expr):
        self.nodeId = nodeId
        self.parents = parents
        self.timestamp = timestamp
        self.expr = expr

    def to_Json(self):
        return {"nodeId": self.nodeId,
                "parents": self.parents,
                "timestamp": self.timestamp,
                "expr": self.expr}
    def __repr__(self):
        return json.dumps(self.to_Json())
class Event (object):
    def __init__(self, idx):
        self.lines = []
        self.idx = idx

    def add_line(self, line):
        self.lines.append(line)

    def to_Node(self):
        return Node(0, 0, self.idx, "".join(self.lines))

def parse(lines):
    timer = 0
    dag = []
    event = Event(idx = timer)
    for line in lines:
        if line.strip()=="":
            if len(event.lines)!=0: #not an empty event
                node = event.to_Node()
                dag.append(node)
            timer+=1
            event = Event(idx = timer)
        else:
            event.add_line(line)

    return dag

if __name__=="__main__":
    with open("/home/nv3le/workspace/saturation-visualization/deepSpacer/pobvis/app/.z3-trace", "r") as f:
        lines = f.readlines()
        dag = parse(lines)
        for n in dag[:10]:
            print(n)
