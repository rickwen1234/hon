# Data Formats

## Sequential Data

Legacy path format:

```text
TraceID Node1 Node2 Node3
```

Timestamped path format:

```text
TraceID Node1@timestamp Node2@timestamp
```

CSV event format:

```csv
trace_id,node_id,timestamp
t1,A,2026-01-01T00:00:00
```

## HON Outputs

Rules:

```text
A B => C 0.8
```

Network edge list:

```csv
from_node,to_node,weight
B|A,"C|B,A",0.8
```

Rule diagnostics:

```csv
order,source_path,target,probability,raw_support,weighted_support,kl_divergence,threshold,weighting_mode
2,A B,C,0.8,10,7.2,0.4,0.2,decay
```

## Multilayer Inputs

Layer edge list:

```csv
source,target,weight
A,B,1.0
```

Dependency list:

```csv
source_layer,source_node,target_layer,target_node,weight
A,u,B,v,1.0
```

Triangle list:

```csv
layer,node1,node2,node3,weight
A,u,v,w,1.0
```

## Cascade Results

```csv
model_name,trial_id,removal_fraction,S_A,S_B,failed_A,failed_B,cascade_steps,q,lambda,mu,theta
peng_cascade,0,0.1,0.82,0.79,18,21,3,0.8,,,
```
