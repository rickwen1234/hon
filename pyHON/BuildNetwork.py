### This file: line-by-line translation from Algorithm 2
### in the paper "Representing higher-order dependencies in networks"
### Code written by Jian Xu, Jan 2017

### Technical questions? Please contact i[at]jianxu[dot]net
### Demo of HON: please visit http://www.HigherOrderNetwork.com
### Latest code: please visit https://github.com/rickwen1234/hon

### Call BuildNetwork()
### Input: Higher-order dependency rules
### Output: HON network
### See details in README


from collections import defaultdict, Counter

Graph = defaultdict(dict)
Verbose = True

def Initialize():
    Graph = defaultdict(dict)


def BuildNetwork(Rules, edge_weight_type="probability", rule_metadata=None):
    VPrint('Building network')
    Initialize()
    SortedSource = sorted(Rules, key=lambda x: len(x))
    for source in SortedSource:
        for target in Rules[source]:
            Graph[source][(target,)] = _edge_weight(Rules, source, target, edge_weight_type, rule_metadata)
            # following operations are destructive to Rules
            if len(source) > 1:
                Rewire(source, (target,))
    RewireTails()
    return Graph

def Rewire(source, target):
    PrevSource = source[:-1]
    PrevTarget = (source[-1],)
    if not PrevSource in Graph or not source in Graph[PrevSource]:
        Graph[PrevSource][source] = Graph[PrevSource][PrevTarget]
        del(Graph[PrevSource][PrevTarget])

def RewireTails():
    ToAdd = []
    ToRemove = []
    for source in Graph:
        for target in Graph[source]:
            if len(target) == 1:
                NewTarget = source + target
                while len(NewTarget) > 1:
                    if NewTarget in Graph:
                        ToAdd.append((source, NewTarget, Graph[source][target]))
                        ToRemove.append((source, target))
                        break
                    else:
                        NewTarget = NewTarget[1:]
    for (source, target, weight) in ToAdd:
        Graph[source][target] = weight
    for (source, target) in ToRemove:
        del(Graph[source][target])


###########################################
# Auxiliary functions
###########################################

def VPrint(string):
    if Verbose:
        print(string)


def _edge_weight(Rules, source, target, edge_weight_type, rule_metadata):
    if edge_weight_type == "probability":
        return Rules[source][target]
    if rule_metadata is None:
        return Rules[source][target]
    metadata = rule_metadata.get((source, target), {})
    if edge_weight_type == "weighted_support":
        return metadata.get("weighted_support", Rules[source][target])
    if edge_weight_type == "raw_support":
        return metadata.get("raw_support", Rules[source][target])
    raise ValueError("Unknown edge_weight_type: " + str(edge_weight_type))
