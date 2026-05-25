# Memory HON audit

- `main.py`: CLI/main entry point. Now detects legacy paths, `Node@timestamp` paths, and CSV event input; passes optional temporal weighting and diagnostics settings through the existing `BuildHON` workflow.
- `BuildRulesFastParameterFree.py`: current fast rule extraction implementation. Added optional weighted transition counts, weighted KL comparison, support selection, and rule diagnostics while preserving raw-count behavior when `weighting_mode="none"`.
- `BuildNetwork.py`: network rewiring implementation. Added optional `edge_weight_type` selection; default remains transition probability.
- `input_parser.py`: isolated parser for legacy and timestamped sequential inputs.
- `temporal_weighting.py`: isolated decay and CogSNet-style memory update functions.
- `../experiments/build_memory_hon.py`: experiment script for FON, original HON, Decay-HON, and Cog-HON construction modes.
