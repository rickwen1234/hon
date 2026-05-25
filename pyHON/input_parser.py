"""Input parsing for legacy and timestamped HON trajectory formats."""

from __future__ import division

import csv

try:
    from temporal_weighting import parse_timestamp
except ImportError:
    from .temporal_weighting import parse_timestamp


def _split_node_timestamp(token):
    if "@" not in token:
        return token, None
    node, timestamp = token.rsplit("@", 1)
    return node, parse_timestamp(timestamp)


def _detect_format(path, delimiter):
    with open(path, newline="") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            lowered = text.lower()
            if "," in text and all(name in lowered for name in ("trace", "node", "timestamp")):
                return "csv_events"
            fields = text.split(delimiter)
            if len(fields) > 1 and any("@" in field for field in fields[1:]):
                return "timestamped_path"
            return "legacy"
    return "legacy"


def read_sequential_data(path, delimiter=" ", input_format="auto", verbose=False):
    """Read legacy paths, node@timestamp paths, or CSV event records.

    The returned records preserve the existing ``[trace_id, movements]`` shape
    when no timestamps are present. Timestamped records add a third element:
    ``[trace_id, movements, timestamps]``.
    """
    fmt = input_format or "auto"
    if fmt == "auto":
        fmt = _detect_format(path, delimiter)
    if fmt in ("csv", "events"):
        fmt = "csv_events"

    if fmt == "csv_events":
        return _read_csv_events(path)
    if fmt == "timestamped_path":
        return _read_timestamped_paths(path, delimiter)
    if fmt == "legacy":
        return _read_legacy_paths(path, delimiter)
    raise ValueError("Unknown input format: {0}".format(input_format))


def _read_legacy_paths(path, delimiter):
    trajectories = []
    with open(path) as handle:
        for line in handle:
            fields = line.strip().split(delimiter)
            if len(fields) < 2:
                continue
            trajectories.append([fields[0], fields[1:]])
    return trajectories


def _read_timestamped_paths(path, delimiter):
    trajectories = []
    with open(path) as handle:
        for line in handle:
            fields = line.strip().split(delimiter)
            if len(fields) < 2:
                continue
            events = [_split_node_timestamp(token) for token in fields[1:]]
            if any(timestamp is None for _, timestamp in events):
                trajectories.append([fields[0], [node for node, _ in events]])
                continue
            events.sort(key=lambda item: item[1])
            trajectories.append([
                fields[0],
                [node for node, _ in events],
                [timestamp for _, timestamp in events],
            ])
    return trajectories


def _read_csv_events(path):
    grouped = {}
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        required = set(["trace_id", "node_id", "timestamp"])
        if not required.issubset(headers):
            raise ValueError("CSV event input requires trace_id,node_id,timestamp columns")
        for row in reader:
            trace_id = row["trace_id"]
            grouped.setdefault(trace_id, []).append((row["node_id"], parse_timestamp(row["timestamp"])))

    trajectories = []
    for trace_id in grouped:
        events = sorted(grouped[trace_id], key=lambda item: item[1])
        trajectories.append([
            trace_id,
            [node for node, _ in events],
            [timestamp for _, timestamp in events],
        ])
    return trajectories
