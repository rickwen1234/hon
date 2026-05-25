### Major update: parameter free and magnitudes faster than previous versions.
### Paper and pseudocode: https://arxiv.org/abs/1712.09658


### This package: Python implementation of the higher-order network (HON) construction algorithm.
### Paper: "Representing higher-order dependencies in networks"
### Code written by Jian Xu, Apr 2017

### Technical questions? Please contact i[at]jianxu[dot]net
### Demo of HON: please visit http://www.HigherOrderNetwork.com
### Latest code: please visit https://github.com/rickwen1234/hon

### See details in README

import BuildRulesFastParameterFree
import BuildRulesFastParameterFreeFreq
import BuildNetwork
import itertools
import argparse
import csv

try:
    from input_parser import read_sequential_data
except ImportError:
    from .input_parser import read_sequential_data



## Initialize algorithm parameters
MaxOrder = 99
MinSupport = 10

## Initialize user parameters
#InputFileName = '../data/traces-simulated-mesh-v100000-t100-mo4.csv'
#OutputRulesFile = '../data/rules-syn.csv'
#OutputNetworkFile = '../data/network-syn.csv'

## Initialize user parameters
#InputFileName = '../../../../C2/data/synthetic/1098_ModifyMixedOrder.csv'
InputFileName = '../data/subpath_30_notime.txt'

#InputFileName = '../data/synthetic-major/9999.csv'
#InputFileName = '../data/synthetic-major/1000_ModifyMixedOrder.csv'
#InputFileName = '../data/traces-test.csv'
#InputFileName = '../data/traces-lloyds.csv'
OutputRulesFile = '../data/rules-cell30.csv'
OutputNetworkFile = '../data/network-cell30.csv'

LastStepsHoldOutForTesting = 0
MinimumLengthForTraining = 1
InputFileDeliminator = ' '
Verbose = True


###########################################
# Functions
###########################################

def ReadSequentialData(InputFileName, input_format='auto'):
    if Verbose:
        print('Reading raw sequential data')
    raw = read_sequential_data(InputFileName, InputFileDeliminator, input_format, Verbose)
    RawTrajectories = []
    for record in raw:
        movements = record[1]
        MinMovementLength = MinimumLengthForTraining + LastStepsHoldOutForTesting
        if len(movements) < MinMovementLength:
            continue
        RawTrajectories.append(record)
    return RawTrajectories


def BuildTrainingAndTesting(RawTrajectories):
    VPrint('Building training and testing')
    Training = []
    Testing = []
    for trajectory in RawTrajectories:
        ship = trajectory[0]
        movement = trajectory[1]
        timestamps = trajectory[2] if len(trajectory) > 2 else None
        movement, timestamps = RemoveAdjacentDuplications(movement, timestamps)
        if LastStepsHoldOutForTesting > 0:
            if timestamps is None:
                Training.append([ship, movement[:-LastStepsHoldOutForTesting]])
            else:
                Training.append([ship, movement[:-LastStepsHoldOutForTesting], timestamps[:-LastStepsHoldOutForTesting]])
            Testing.append([ship, movement[-LastStepsHoldOutForTesting]])
        else:
            if timestamps is None:
                Training.append([ship, movement])
            else:
                Training.append([ship, movement, timestamps])
    return Training, Testing


def RemoveAdjacentDuplications(movement, timestamps=None):
    filtered = []
    filtered_timestamps = [] if timestamps is not None else None
    previous = None
    for index, node in enumerate(movement):
        if index == 0 or node != previous:
            filtered.append(node)
            if timestamps is not None:
                filtered_timestamps.append(timestamps[index])
        previous = node
    return filtered, filtered_timestamps

def DumpRules(Rules, OutputRulesFile):
    VPrint('Dumping rules to file')
    with open(OutputRulesFile, 'w') as f:
        for Source in Rules:
            for Target in Rules[Source]:
                f.write(' '.join([' '.join([str(x) for x in Source]), '=>', Target, str(Rules[Source][Target])]) + '\n')

def DumpNetwork(Network, OutputNetworkFile):
    VPrint('Dumping network to file')
    LineCount = 0
    with open(OutputNetworkFile, 'w') as f:
        for source in Network:
            for target in Network[source]:
                f.write(','.join([SequenceToNode(source), SequenceToNode(target), str(Network[source][target])]) + '\n')
                LineCount += 1
    VPrint(str(LineCount) + ' lines written.')


def DumpRuleDiagnostics(diagnostics, output_file):
    if not output_file:
        return
    VPrint('Dumping weighted rule diagnostics to file')
    fields = [
        'order',
        'source_path',
        'target',
        'probability',
        'raw_support',
        'weighted_support',
        'base_weighted_support',
        'kl_divergence',
        'threshold',
        'first_timestamp',
        'last_timestamp',
        'weighting_mode',
    ]
    with open(output_file, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in diagnostics:
            writer.writerow(row)

def SequenceToNode(seq):
    curr = seq[-1]
    node = curr + '|'
    seq = seq[:-1]
    while len(seq) > 0:
        curr = seq[-1]
        node = node + curr + '.'
        seq = seq[:-1]
    if node[-1] == '.':
        return node[:-1]
    else:
        return node

def VPrint(string):
    if Verbose:
        print(string)


def BuildHON(InputFileName, OutputNetworkFile, max_order=None, min_support=None,
             weighting_mode='none', decay_mode='exp', lambda_=0.0, mu=0.5,
             theta=0.0, analysis_time=None, input_format='auto',
             support_type='raw', debug_weighted_rules=False,
             diagnostics_file=None, edge_weight_type='probability'):
    RawTrajectories = ReadSequentialData(InputFileName, input_format)
    TrainingTrajectory, TestingTrajectory = BuildTrainingAndTesting(RawTrajectories)
    VPrint(len(TrainingTrajectory))
    Rules = BuildRulesFastParameterFree.ExtractRules(
        TrainingTrajectory,
        max_order or MaxOrder,
        min_support or MinSupport,
        weighting_mode=weighting_mode,
        decay_mode=decay_mode,
        lambda_=lambda_,
        mu=mu,
        theta=theta,
        analysis_time=analysis_time,
        support_type=support_type,
        output_diagnostics=debug_weighted_rules or diagnostics_file is not None,
    )
    # DumpRules(Rules, OutputRulesFile)
    Network = BuildNetwork.BuildNetwork(
        Rules,
        edge_weight_type=edge_weight_type,
        rule_metadata=BuildRulesFastParameterFree.RuleMetadata,
    )
    DumpNetwork(Network, OutputNetworkFile)
    if debug_weighted_rules or diagnostics_file:
        path = diagnostics_file or OutputNetworkFile + '.weighted-rules.csv'
        DumpRuleDiagnostics(BuildRulesFastParameterFree.RuleDiagnostics, path)
    VPrint('Done: '+InputFileName)
    return Rules, Network

def BuildHONfreq(InputFileName, OutputNetworkFile, input_format='auto'):
    print('FREQ mode!!!!!!')
    RawTrajectories = ReadSequentialData(InputFileName, input_format)
    TrainingTrajectory, TestingTrajectory = BuildTrainingAndTesting(RawTrajectories)
    VPrint(len(TrainingTrajectory))
    Rules = BuildRulesFastParameterFreeFreq.ExtractRules(TrainingTrajectory, MaxOrder, MinSupport)
    # DumpRules(Rules, OutputRulesFile)
    Network = BuildNetwork.BuildNetwork(Rules)
    DumpNetwork(Network, OutputNetworkFile)
    VPrint('Done: '+InputFileName)


def ParseArguments():
    parser = argparse.ArgumentParser(description='Build a higher-order network from sequential data.')
    parser.add_argument('--input', default=InputFileName)
    parser.add_argument('--output-network', default=OutputNetworkFile)
    parser.add_argument('--output-rules', default=OutputRulesFile)
    parser.add_argument('--max-order', type=int, default=MaxOrder)
    parser.add_argument('--min-support', type=float, default=MinSupport)
    parser.add_argument('--input-format', default='auto',
                        choices=['auto', 'legacy', 'timestamped_path', 'csv_events', 'csv', 'events'])
    parser.add_argument('--weighting-mode', default='none', choices=['none', 'decay', 'cogsnet'])
    parser.add_argument('--decay-mode', default='exp', choices=['none', 'exp', 'power', 'linear'])
    parser.add_argument('--lambda', dest='lambda_', type=float, default=0.0)
    parser.add_argument('--mu', type=float, default=0.5)
    parser.add_argument('--theta', type=float, default=0.0)
    parser.add_argument('--analysis-time', default=None)
    parser.add_argument('--support-type', default='raw', choices=['raw', 'weighted'])
    parser.add_argument('--edge-weight-type', default='probability',
                        choices=['probability', 'weighted_support', 'raw_support'])
    parser.add_argument('--debug-weighted-rules', action='store_true')
    parser.add_argument('--diagnostics-file', default=None)
    parser.add_argument('--freq', action='store_true')
    return parser.parse_args()

###########################################
# Main function
###########################################

if __name__ == "__main__":
    args = ParseArguments()
    if args.freq:
        BuildHONfreq(args.input, args.output_network, args.input_format)
    else:
        Rules, Network = BuildHON(
            args.input,
            args.output_network,
            max_order=args.max_order,
            min_support=args.min_support,
            weighting_mode=args.weighting_mode,
            decay_mode=args.decay_mode,
            lambda_=args.lambda_,
            mu=args.mu,
            theta=args.theta,
            analysis_time=args.analysis_time,
            input_format=args.input_format,
            support_type=args.support_type,
            debug_weighted_rules=args.debug_weighted_rules,
            diagnostics_file=args.diagnostics_file,
            edge_weight_type=args.edge_weight_type,
        )
        DumpRules(Rules, args.output_rules)
