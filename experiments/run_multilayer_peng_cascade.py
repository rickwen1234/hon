"""Prepare Peng-style cascade inputs from an exported multilayer network."""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from multilayer import MultiLayerNetwork
from multilayer.cascade_adapter import export_peng_cascade_inputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Peng cascade input files.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--layer-a", required=True)
    parser.add_argument("--layer-b", required=True)
    parser.add_argument("--cascade-output-dir", required=True)
    parser.add_argument("--run-cascade", action="store_true")
    args = parser.parse_args()
    mln = MultiLayerNetwork.load(args.input_dir)
    export_peng_cascade_inputs(mln, args.cascade_output_dir, args.layer_a, args.layer_b)
    if args.run_cascade:
        print("No integrated Peng cascade runner was detected; prepared inputs only.")
    print("Wrote Peng cascade inputs to {0}".format(args.cascade_output_dir))


if __name__ == "__main__":
    main()
