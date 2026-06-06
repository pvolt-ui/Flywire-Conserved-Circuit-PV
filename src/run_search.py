"""
run_search.py — driver: run the three tiers on a dataset triple, verify exactly.

Usage:  python run_search.py FAFB BANC MCNS
"""
from __future__ import annotations
import sys
import time
import numpy as np

from io_utils import build_clean
from graph_core import DiGraph
from iso_utils import is_iso
from match_engine import (greedy_independent_set, max_induced_out_star,
                          grow_common_subgraph)


def load(ds):
    nodes, edges = build_clean(ds)
    return nodes, DiGraph(len(nodes), edges)


def verify_triple(graphs, matched):
    """Confirm induced subgraphs are mutually isomorphic in the matched order
    (identical adjacency = strongest form). Returns (identical, pairwise_iso, adj0)."""
    A = [g.induced_adcmatrix(m) for g, m in zip(graphs, matched)]
    identical = all(np.array_equal(A[0], A[i]) for i in range(1, len(A)))
    pall = all(is_iso(A[0], A[i]) for i in range(1, len(A)))
    return identical, pall, A[0]


def main():
    triple = sys.argv[1:4] if len(sys.argv) >= 4 else ["FAFB", "BANC", "MCNS"]
    print(f"Triple: {triple}")
    t0 = time.time()
    loaded = [load(ds) for ds in triple]
    graphs = [x[1] for x in loaded]
    print(f"loaded in {time.time()-t0:.1f}s")

    # ---- Tier 0: common independent set (trivial) ----
    iset_sizes = [len(greedy_independent_set(g, cap=8000)) for g in graphs]
    print(f"\n[Tier 0] greedy independent-set sizes (capped 8000): {iset_sizes}")
    print(f"[Tier 0] common independent set N (trivial, empty graph) >= {min(iset_sizes)}")

    # ---- Tier 1: common induced out-star ----
    stars = [max_induced_out_star(g, n_hubs_try=40) for g in graphs]
    star_sizes = [len(s) for s in stars]
    n_star = min(star_sizes)
    matched_star = [s[:n_star] for s in stars]  # hub first, then n_star-1 leaves
    ident, piso, A = verify_triple(graphs, matched_star)
    print(f"\n[Tier 1] per-graph max out-star sizes: {star_sizes}")
    print(f"[Tier 1] common out-star N = {n_star}  edges={int(A.sum())}  "
          f"identical={ident} iso={piso}")

    # ---- Tier 2: richly-connected common induced subgraph ----
    sigsets = []
    for g in graphs:
        sig = {}
        for i in range(g.n):
            sig.setdefault((int(g.indeg[i]), int(g.outdeg[i])), []).append(i)
        sigsets.append(sig)
    common_sigs = set(sigsets[0]) & set(sigsets[1]) & set(sigsets[2])
    cand_sigs = sorted(common_sigs, key=lambda s: -(s[0] + s[1]))
    cand_sigs = [s for s in cand_sigs if 4 <= s[0] + s[1] <= 40][:30]
    print(f"\n[Tier 2] trying {len(cand_sigs)} shared degree-signatures as seeds...")
    best = None
    best_info = None
    for s in cand_sigs:
        seeds = [sigsets[gi][s][0] for gi in range(3)]
        matched = grow_common_subgraph(graphs, seeds, max_n=50)
        n = len(matched[0])
        if best is None or n > len(best[0]):
            ident, piso, A = verify_triple(graphs, matched)
            if ident:
                best = matched
                best_info = (n, int(A.sum()), ident, piso)
    if best is not None:
        n, e, ident, piso = best_info
        print(f"[Tier 2] best richly-connected common subgraph: N={n} edges={e} "
              f"identical={ident} iso={piso}")
    else:
        print("[Tier 2] no connected match grown from these seeds")
    print(f"\ntotal {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
