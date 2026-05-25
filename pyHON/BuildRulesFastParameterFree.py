### Major update: parameter free and magnitudes faster than previous versions.
### Paper and pseudocode: https://arxiv.org/abs/1712.09658

### This file: line-by-line translation from Algorithm 1
### in the paper "Representing higher-order dependencies in networks"
### Code written by Jian Xu, Apr 2017

### Technical questions? Please contact i[at]jianxu[dot]net
### Demo of HON: please visit http://www.HigherOrderNetwork.com
### Latest code: please visit https://github.com/rickwen1234/hon

### Call ExtractRules()
### Input: Trajectory
### Output: Higher-order dependency rules
### See details in README

from collections import defaultdict, Counter
#from concurrent import futures

import math

try:
    from temporal_weighting import decay_weight, cogsnet_update, parse_timestamp
except ImportError:
    from .temporal_weighting import decay_weight, cogsnet_update, parse_timestamp

ThresholdMultiplier = 1

Count = defaultdict(lambda: defaultdict(int))
WeightedCount = defaultdict(lambda: defaultdict(float))
Rules = defaultdict(dict)
Distribution = defaultdict(dict)
SourceToExtSource = defaultdict(set)
divergences = []
Verbose = True
StartingPoints = defaultdict(set)
Trajectory = []
MinSupport = 1
WeightingMode = "none"
DecayMode = "exp"
Lambda = 0.0
Mu = 0.5
Theta = 0.0
AnalysisTime = None
SupportType = "raw"
RuleDiagnostics = []
RuleMetadata = {}
LastObservationTimestamp = {}
ComparisonDiagnostics = {}
EPS = 1e-12

def Initialize():
    global Count
    global WeightedCount
    global Rules
    global Distribution
    global SourceToExtSource
    global StartingPoints
    global RuleDiagnostics
    global RuleMetadata
    global LastObservationTimestamp
    global ComparisonDiagnostics

    Count = defaultdict(lambda: defaultdict(int))
    WeightedCount = defaultdict(lambda: defaultdict(float))
    Rules = defaultdict(dict)
    Distribution = defaultdict(dict)
    SourceToExtSource = defaultdict(set)
    StartingPoints = defaultdict(set)
    RuleDiagnostics = []
    RuleMetadata = {}
    LastObservationTimestamp = {}
    ComparisonDiagnostics = {}

def ExtractRules(T, MaxOrder, MS, weighting_mode="none", decay_mode="exp",
                 lambda_=0.0, mu=0.5, theta=0.0, analysis_time=None,
                 support_type="raw", output_diagnostics=False):
    Initialize()
    global Trajectory
    global MinSupport
    global WeightingMode
    global DecayMode
    global Lambda
    global Mu
    global Theta
    global AnalysisTime
    global SupportType
    Trajectory = T
    MinSupport = MS
    WeightingMode = weighting_mode or "none"
    DecayMode = decay_mode or "exp"
    Lambda = float(lambda_)
    Mu = float(mu)
    Theta = float(theta)
    AnalysisTime = _resolve_analysis_time(T, analysis_time)
    SupportType = support_type or "raw"
    BuildOrder(1, Trajectory, MinSupport)
    GenerateAllRules(MaxOrder, Trajectory, MinSupport)
    if output_diagnostics:
        _build_rule_diagnostics()
    #DumpDivergences()
    return Rules


def BuildOrder(order, Trajectory, MinSupport):

    BuildObservations(Trajectory, order)
    BuildDistributions(MinSupport, order)
    #BuildSourceToExtSource(order)  # to speed up lookups
    #ObservationBuiltForOrder.add(order)


def BuildObservations(Trajectory, order):
    VPrint('building observations for order ' + str(order))
    LoopCounter = 0
    observations = []
    for Tindex in range(len(Trajectory)):
        LoopCounter += 1
        if LoopCounter % 10000 == 0:
            VPrint(LoopCounter)
        # remove metadata stored in the first element
        # this step can be extended to incorporate richer information
        trajectory = Trajectory[Tindex][1]

        for index in range(len(trajectory) - order):
            Source = tuple(trajectory[index:index+order])
            Target = trajectory[index+order]
            timestamp = _transition_timestamp(Trajectory[Tindex], index + order)
            observations.append((Source, Target, timestamp))
            StartingPoints[Source].add((Tindex, index))
    _add_observations(observations)

        # SubSequence = ExtractSubSequences(trajectory, order)
        # for sequence in SubSequence:
        #     Target = sequence[-1]
        #     Source = sequence[:-1]
        #     IncreaseCounter(Source, Target)


def BuildDistributions(MinSupport, order):
    VPrint('building distributions with MinSupport ' + str(MinSupport) +' and threshold multiplier ' + str(ThresholdMultiplier))
    for Source in Count:
        if len(Source) == order:
            for Target in Count[Source].keys():
                if _support(Source, Target) < MinSupport:
                    Count[Source][Target] = 0
                    WeightedCount[Source][Target] = 0.0
            total = _total_support(Source)
            for Target in Count[Source]:
                if _effective_count(Source, Target) > 0 and total > 0:
                    Distribution[Source][Target] = 1.0 * _effective_count(Source, Target) / total


def GenerateAllRules(MaxOrder, Trajectory, MinSupport):
    VPrint('generating rules')
    progress = len(Distribution)
    VPrint(progress)
    LoopCounter = 0
    for Source in tuple(Distribution.keys()):
        AddToRules(Source)
        ExtendRule(Source, Source, 1, MaxOrder, Trajectory, MinSupport)
        LoopCounter += 1
        if LoopCounter % 10 == 0:
            VPrint('generating rules ' + str(LoopCounter) + ' ' + str(progress))


def ExtendRule(Valid, Curr, order, MaxOrder, Trajectory, MinSupport):
    if order >= MaxOrder:
        AddToRules(Valid)
    else:
        Distr = Distribution[Valid]
        # test if divergence has no chance exceeding the threshold when going for higher order
        #print(KLD(MaxDivergence(Distribution[Curr]), Distr), KLDThreshold(order+1, Curr))
        if KLD(MaxDivergence(Distribution[Curr]), Distr) < KLDThreshold(order+1, Curr):
            AddToRules(Valid)
        else:
            NewOrder = order + 1
            #if NewOrder not in ObservationBuiltForOrder:
            #    BuildOrder(NewOrder, Trajectory, MinSupport)
            #    VPrint(str(KLD(MaxDivergence(Distribution[Curr]), Distr)) + ' ' + str(KLDThreshold(order+1, Curr)))
            Extended = ExtendSourceFast(Curr)
            if len(Extended) == 0:
                AddToRules(Valid)
            else:
                for ExtSource in Extended:
                    ExtDistr = Distribution[ExtSource]  # Pseudocode in Algorithm 1 has a typo here
                    divergence = KLD(ExtDistr, Distr)
                    #divergences.append((NewOrder, ExtSource, Valid, divergence))
                    threshold = KLDThreshold(NewOrder, ExtSource)
                    _record_diagnostics(ExtSource, Valid, divergence, threshold)
                    if divergence > threshold:
                        # higher-order dependencies exist for order NewOrder
                        # keep comparing probability distribution of higher orders with current order
                        ExtendRule(ExtSource, ExtSource, NewOrder, MaxOrder, Trajectory, MinSupport)
                    else:
                        # higher-order dependencies do not exist for current order
                        # keep comparing probability distribution of higher orders with known order
                        ExtendRule(Valid, ExtSource, NewOrder, MaxOrder, Trajectory, MinSupport)


def MaxDivergence(Distr):
    MaxValKey = sorted(Distr, key=Distr.__getitem__)
    d = {MaxValKey[0]: 1}
    return d


def AddToRules(Source):
    for order in range(1, len(Source)+1):
        s = Source[0:order]
        #print(s, Source)
        if not s in Distribution or len(Distribution[s]) == 0:
            ExtendSourceFast(s[1:])
        Rules[s] = Distribution[s]
        for target in Distribution[s]:
            RuleMetadata[(s, target)] = {
                "probability": Distribution[s][target],
                "raw_support": Count[s][target],
                "weighted_support": WeightedCount[s][target],
            }
    # while len(Source) > 0:
    #     # To output frequencies instead of probabilities, change "Distribution" to "Count"
    #     # and filter out zero values
    #     if not Source in Distribution:
    #         ExtendSourceFast(Source[1:])
    #     Rules[Source] = Distribution[Source]
    #     PrevSource = Source[:-1]
    #     AddToRules(PrevSource)

###########################################
# Auxiliary functions
###########################################


def ExtractSubSequences(trajectory, order):
    SubSequence = []
    for starting in range(len(trajectory) - order + 1):
        SubSequence.append(tuple(trajectory[starting:starting + order]))
    return SubSequence


#def IncreaseCounter(Source, Target):
    #if not Source in Count:
    #    Count[Source] = Counter()
    #Count[Source][Target] += 1


def ExtendSourceSlow(Curr, NewOrder):
    Extended = []
    for CandidateSource in Distribution:
        if len(CandidateSource) == NewOrder and CandidateSource[-len(Curr):] == Curr:
            Extended.append(CandidateSource)
    return Extended


def ExtendSource(Curr, NewOrder):
    if Curr in SourceToExtSource:
        if NewOrder in SourceToExtSource[Curr]:
            return SourceToExtSource[Curr][NewOrder]
    return []


def ExtendSourceFast(Curr):
    if Curr in SourceToExtSource:
        return SourceToExtSource[Curr]
    else:
        ExtendObservation(Curr)
        if Curr in SourceToExtSource:
            return SourceToExtSource[Curr]
        else:
            return []


def ExtendObservation(Source):
    #print(Source)
    # if len(Source) == 1:
    #     # build SourceToExtSource
    #     C = defaultdict(lambda: defaultdict(int))
    #     for Tindex, index in StartingPoints[Source]:
    #         if index-1 >= 0 and index+1 < len(Trajectory[Tindex][1]):
    #             ExtSource = tuple(Trajectory[Tindex][1][index-1:index+1])
    #             Target = Trajectory[Tindex][1][index+1]
    #             C[ExtSource][Target] += 1
    #             StartingPoints[ExtSource].add((Tindex, index-1))
    #     if len(C) == 0:
    #         return
    #     for s in C:
    #         for t in C[s]:
    #             if C[s][t] < MinSupport:
    #                 C[s][t] = 0
    #             Count[s][t] += C[s][t]
    #         CsSupport = sum(C[s].values())
    #         for t in C[s]:
    #             if C[s][t] > 0:
    #                 Distribution[s][t] = 1.0 * C[s][t] / CsSupport
    #                 SourceToExtSource[s[1:]].add(s)
    # else:
    #print(Source)
    if len(Source) > 1:
        if (not Source[1:] in Count) or (len(Count[Source]) == 0):
            ExtendObservation(Source[1:])
    order = len(Source)
    C = defaultdict(lambda: defaultdict(list))
    #print(len(StartingPoints[Source]))
    # if len(StartingPoints[Source]) > 1000:
    #     with futures.ThreadPoolExecutor() as executor:
    #         Cs = executor.map(SubExtendObservation, [(x, order) for x in StartingPoints[Source]], chunksize=100)
    #         for c in Cs:
    #             for s in c:
    #                 for t in c[s]:
    #                     C[s][t] += c[s][t]
    # else:
    for Tindex, index in StartingPoints[Source]:
        if index - 1 >= 0 and index + order < len(Trajectory[Tindex][1]):
            ExtSource = tuple(Trajectory[Tindex][1][index - 1:index + order])
            Target = Trajectory[Tindex][1][index + order]
            timestamp = _transition_timestamp(Trajectory[Tindex], index + order)
            C[ExtSource][Target].append(timestamp)
            StartingPoints[ExtSource].add((Tindex, index - 1))

    if len(C) == 0:
        return
    for s in C:
        observations = []
        for t in C[s]:
            for timestamp in C[s][t]:
                observations.append((s, t, timestamp))
        _add_observations(observations)
        for t in C[s]:
            if _support(s, t) < MinSupport:
                Count[s][t] = 0
                WeightedCount[s][t] = 0.0
        CsSupport = _total_support(s)
        for t in C[s]:
            if _effective_count(s, t) > 0 and CsSupport > 0:
                Distribution[s][t] = 1.0 * _effective_count(s, t) / CsSupport
                SourceToExtSource[s[1:]].add(s)


def SubExtendObservation(param):
    global Trajectory
    C = defaultdict(lambda: defaultdict(int))
    p, order = param
    Tindex, index = p
    if index - 1 >= 0 and index + order < len(Trajectory[Tindex][1]):
        ExtSource = tuple(Trajectory[Tindex][1][index - 1:index + order])
        Target = Trajectory[Tindex][1][index + order]
        C[ExtSource][Target] += 1
        StartingPoints[ExtSource].add((Tindex, index - 1))
    #print(C)
    return C


# creating a cache for fast lookup
def BuildSourceToExtSource(order):
    VPrint('Building cache')
    for source in Distribution:
        if len(source) == order:
            if len(source) > 1:
                NewOrder = len(source)
                for starting in range(1, len(source)):
                    curr = source[starting:]
                    if not curr in SourceToExtSource:
                        SourceToExtSource[curr] = {}
                    if not NewOrder in SourceToExtSource[curr]:
                        SourceToExtSource[curr][NewOrder] = set()
                    SourceToExtSource[curr][NewOrder].add(source)


def VPrint(string):
    if Verbose:
        print(string)


def KLD(a, b):
    divergence = 0
    for target in a:
        pa = GetProbability(a, target)
        pb = GetProbability(b, target)
        if WeightingMode == "none":
            divergence += pa * math.log((pa/pb), 2)
        else:
            divergence += pa * math.log((pa + EPS) / (pb + EPS), 2)
    return divergence


def KLDThreshold(NewOrder, ExtSource):
    support = _threshold_support(ExtSource)
    if support <= 0:
        support = EPS
    return ThresholdMultiplier * NewOrder / math.log(1 + support, 2) # typo in Pseudocode in Algorithm 1


def GetProbability(d, key):
    if key not in d:
        return 0
    else:
        return d[key]


def DumpDivergences():
    with open('divergences.csv', 'w') as f:
        for pair in divergences:
            f.write(';'.join(map(str, pair)) + '\n')


def _add_observations(observations):
    if WeightingMode == "none":
        for source, target, timestamp in observations:
            Count[source][target] += 1
            WeightedCount[source][target] += 1.0
        return

    grouped = defaultdict(list)
    for source, target, timestamp in observations:
        Count[source][target] += 1
        grouped[(source, target)].append(timestamp)

    if WeightingMode == "decay":
        for source, target in grouped:
            for timestamp in grouped[(source, target)]:
                WeightedCount[source][target] += decay_weight(_delta_to_analysis(timestamp), DecayMode, Lambda)
    elif WeightingMode == "cogsnet":
        for source, target in grouped:
            previous_timestamp = LastObservationTimestamp.get((source, target))
            weight = WeightedCount[source][target]
            for timestamp in sorted(grouped[(source, target)], key=lambda value: -float("inf") if value is None else value):
                delta_t = None if previous_timestamp is None or timestamp is None else timestamp - previous_timestamp
                weight = cogsnet_update(weight, delta_t, Mu, Theta, Lambda, DecayMode)
                previous_timestamp = timestamp
            WeightedCount[source][target] = weight
            LastObservationTimestamp[(source, target)] = previous_timestamp
    else:
        raise ValueError("Unknown weighting_mode: " + str(WeightingMode))


def _effective_count(source, target):
    if WeightingMode == "none":
        return Count[source][target]
    return WeightedCount[source][target]


def _total_support(source):
    if WeightingMode == "none":
        return sum(Count[source].values())
    return sum(WeightedCount[source].values())


def _support(source, target):
    if SupportType == "weighted" and WeightingMode != "none":
        return WeightedCount[source][target]
    return Count[source][target]


def _threshold_support(source):
    if SupportType == "weighted" and WeightingMode != "none":
        return sum(WeightedCount[source].values())
    return sum(Count[source].values())


def _transition_timestamp(record, event_index):
    if len(record) < 3:
        return None
    timestamps = record[2]
    if event_index < len(timestamps):
        return timestamps[event_index]
    return None


def _resolve_analysis_time(trajectory, analysis_time):
    if analysis_time is not None:
        return parse_timestamp(analysis_time)
    latest = None
    for record in trajectory:
        if len(record) < 3:
            continue
        for timestamp in record[2]:
            if latest is None or timestamp > latest:
                latest = timestamp
    return latest


def _delta_to_analysis(timestamp):
    if timestamp is None or AnalysisTime is None:
        return None
    return max(0.0, AnalysisTime - timestamp)


def _record_diagnostics(source, base_source, divergence, threshold):
    ComparisonDiagnostics[source] = {
        "base_weighted_support": sum(WeightedCount[base_source].values()),
        "kl_divergence": divergence,
        "threshold": threshold,
    }


def _build_rule_diagnostics():
    RuleDiagnostics[:] = []
    for source in Rules:
        comparison = ComparisonDiagnostics.get(source, {})
        for target in Rules[source]:
            RuleDiagnostics.append({
                "order": len(source),
                "source_path": " ".join([str(x) for x in source]),
                "target": target,
                "probability": Distribution[source][target],
                "raw_support": Count[source][target],
                "weighted_support": WeightedCount[source][target],
                "base_weighted_support": comparison.get("base_weighted_support", ""),
                "kl_divergence": comparison.get("kl_divergence", ""),
                "threshold": comparison.get("threshold", ""),
                "first_timestamp": _first_timestamp(source, target),
                "last_timestamp": _last_timestamp(source, target),
                "weighting_mode": WeightingMode,
            })


def _first_timestamp(source, target):
    values = _timestamps_for(source, target)
    return "" if len(values) == 0 else min(values)


def _last_timestamp(source, target):
    values = _timestamps_for(source, target)
    return "" if len(values) == 0 else max(values)


def _timestamps_for(source, target):
    timestamps = []
    order = len(source)
    for record in Trajectory:
        trajectory = record[1]
        for index in range(len(trajectory) - order):
            if tuple(trajectory[index:index + order]) == source and trajectory[index + order] == target:
                timestamp = _transition_timestamp(record, index + order)
                if timestamp is not None:
                    timestamps.append(timestamp)
    return timestamps
