#!/usr/bin/env python
"""
run.py — CANONICAL entrypoint for the conserved-circuit submission.

This is the single script that regenerates the headline deliverable:
    network.csv                              (3 x 169 matched neuron IDs)
    results/headline_typed.json              (per-row IDs, cell types, NT)
    results/headline_typed_adjacency.npy     (the 169x169 conserved adjacency)

It runs the APL-seeded, cell-type-constrained common-subgraph growth across
FAFB + BANC + MCNS and extracts the rich 2-core / largest weakly-connected circuit.
The search is deterministic, so a clean run reproduces the committed artifact exactly.

The scripts in src/find_circuit*.py are earlier frontier stages (structural-only N=37,
typed seed-sweep) kept for the degeneracy-frontier analysis; THIS script is the only
canonical producer of network.csv. Downstream analyses (significance, corroboration,
maximal set) read the artifacts this script writes:
    python src/null_model.py 10000
    python src/connectivity_stats.py
    python src/maximal_set.py

Usage:  python run.py
"""
import os
import sys
import runpy

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

if __name__ == "__main__":
    # Execute the canonical growth pipeline (src/grow_apl.py) as __main__.
    runpy.run_path(os.path.join(ROOT, "src", "grow_apl.py"), run_name="__main__")
