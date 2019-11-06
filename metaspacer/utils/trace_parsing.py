"""A parser for vampire output."""

import logging
import re
from collections import namedtuple
import json
from enum import Enum

class EType(Enum):
    EXP_LVL = 0
    EXP_POB = 1
    ADD_LEM = 2
    PRO_LEM = 3
    NA = 4
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
    def __init__(self, nodeId, parent, event_type,  timestamp, expr):
        self.nodeId = nodeId
        self.parent = parent
        self.event_type = event_type
        self.timestamp = timestamp
        self.expr = expr

    def to_Json(self):
        return {"nodeId": self.nodeId,
                "parent": self.parent,
                "event_type": str(self.event_type),
                "timestamp": self.timestamp,
                "expr": self.expr}
    def __repr__(self):
        return json.dumps(self.to_Json())
class Event (object):
    def __init__(self, idx, parent = None):
        self.lines = []
        self.idx = idx
        self.event_type = EType.NA
        self.parent = None

    def add_line(self, line):
        self.lines.append(line)

    def to_Node(self):
        return Node(self.idx, self.parent, self.event_type, self.idx, "".join(self.lines))

    def finalize(self, all_events):
        if self.lines[0].startswith("* LEVEL"):
            self.event_type = EType.EXP_LVL
        elif self.lines[0].startswith("** expand-pob"):
            self.event_type = EType.EXP_POB
            _, _, _, _, level, _, depth = self.lines[0].strip().split()
            self.level = int(level)
            self.depth = int(depth)
 
        elif self.lines[0].startswith("** add-lemma"):
            self.event_type = EType.ADD_LEM
        elif self.lines[0].startswith("Propagating"):
            self.event_type = EType.PRO_LEM
        self.parent = self.find_parent(all_events).idx

    def find_parent(self, all_events):
        if self.event_type == EType.ADD_LEM:
            #Adding lemma is the child event of the latest EXP_POB or Propagating
            if all_events[-1].event_type == EType.EXP_POB:
                return all_events[-1]
            else:
                for e in reversed(all_events):
                    if e.event_type == EType.PRO_LEM:
                        return e
        elif self.event_type == EType.EXP_POB:
            #Find the latest one with greater depth
            for e in reversed(all_events):
                if e.event_type == EType.EXP_LVL or ( e.event_type == EType.EXP_POB and e.depth > self.depth):
                    return e
            print(self.lines)
            print("no father pob!!!!")
           
        elif self.event_type == EType.PRO_LEM:
            #Propagating is the child event of the latest EXP_LVL event
            for e in reversed(all_events):
                if e.event_type == EType.EXP_LVL:
                    return e

        return all_events[0]



    def to_Json(self):
        return {"nodeId": self.idx,
                "parent": self.parent,
                "event_type": str(self.event_type),
                "expr": self.lines}

def parse(lines):
    timer = 0
    all_events = [Event(-1)]
    event = Event(idx = timer)

    for line in lines:
        if line.strip()=="":
            if len(event.lines)!=0: #not an empty event
                event.finalize(all_events)
                all_events.append(event)
            timer+=1
            event = Event(idx = timer)
            
        else:
            event.add_line(line)

    spacer_nodes = []
    for event in all_events:
        
        spacer_nodes.append(event.to_Json())

    return spacer_nodes

if __name__=="__main__":
    with open("/home/nv3le/workspace/saturation-visualization/deepSpacer/pobvis/app/.z3-trace", "r") as f:
        lines = f.readlines()
        all_events = parse(lines)
        print(len(all_events))
        # for e in all_events[:10]:
        #     print(e.to_Node())

