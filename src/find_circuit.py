"""
find_circuit.py — end-to-end: find the conserved circuit across a dataset triple,
extract a real-circuit core (2-core, largest connected component), verify exactly,
and cross-check the biology (cell types / neurotransmitters) across all three.

Usage:  python find_circuit.py FAFB BANC MCNS
Writes: results/frontier.json, results/headline_circuit.json,
        network.csv (root IDs, columns = datasets, rows = matched neurons).
"""
from __future__ import annotations
import sys, os, json, time
import numpy as np

from io_utils import build_clean, ROOT
from graph_core import DiGraph
from iso_utils import is_iso
from annotate import load_annotations
from match_engine import (greedy_independent_set, max_induced_out_star,
                          grow_common_subgraph, two_core_positions,
                          largest_weak_component_positions)


def adj(g, m):
    return g.induced_adcmatrix(m)


def main():
    triple = sys.argv[1:4] if len(sys.argv) >= 4 else ["FAFB", "BANC", "MCNS"]
    t0 = time.time()
    nodes, graphs, anns = [], [], []
    for ds in triple:
        nd, ed = build_clean(ds)
        nodes.append(nd)
        graphs.append(DiGraph(len(nd), ed))
        ann, _ = load_annotations(ds)
        anns.append(ann)
    print(f"loaded triple {triple} + annotations ({time.time()-t0:.1f}s)", flush=True)

    frontier = {"triple": triple}

    # Tier 0
    iset = [len(greedy_independent_set(g, cap=20000)) for g in graphs]
    frontier["tier0_independent_set_min"] = int(min(iset))
    print(f"[Tier0] independent set sizes {iset} -> common >= {min(iset)}", flush=True)

    # Tier 1
    stars = [max_induced_out_star(g, n_hubs_try=40) for g in graphs]
    n_star = min(len(s) for s in stars)
    mstar = [s[:n_star] for s in stars]
    A = adj(graphs[0], mstar[0])
    ok_star = all(np.array_equal(A, adj(graphs[i], mstar[i])) for i in (1, 2))
    frontier["tier1_outstar_N"] = int(n_star)
    frontier["tier1_outstar_identical"] = bool(ok_star)
    print(f"[Tier1] out-star N={n_star} identical={ok_star}", flush=True)

    # Tier 2: rich growth over many shared-degree-signature seeds
    sigsets = []
    for g in graphs:
        d = {}
        for i in range(g.n):
            d.setdefault((int(g.indeg[i]), int(g.outdeg[i])), []).append(i)
        sigsets.append(d)
    common = set(sigsets[0]) & set(sigsets[1]) & set(sigsets[2])
    cand = sorted([s for s in common if 6 <= s[0] + s[1] <= 80],
                  key=lambda s: -(s[0] + s[1]))[:80]
    print(f"[Tier2] {len(cand)} seed signatures", flush=True)

    best = None  # (core_wcc_size, full_N, matched, core_positions)
    t = time.time()
    for s in cand:
        seeds = [sigsets[gi][s][0] for gi in range(3)]
        m = grow_common_subgraph(graphs, seeds, max_n=140, strategy="rich",
                                 frontier_cap=2000)
        A0 = adj(graphs[0], m[0])
        core = two_core_positions(A0)
        if core.size:
            wcc = largest_weak_component_positions(A0[np.ix_(core, core)])
            corepos = core[wcc]
        else:
            corepos = core
        score = corepos.size
        if best is None or score > best[0]:
            best = (int(score), len(m[0]), m, corepos)
    core_size, full_n, m, corepos = best
    print(f"[Tier2] best: full_N={full_n} circuit(2-core WCC)={core_size} "
          f"({time.time()-t:.1f}s)", flush=True)

    # Headline circuit = the 2-core largest-WCC sub-correspondence.
    matched_core = [[m[gi][p] for p in corepos.tolist()] for gi in range(3)]
    Ac = [adj(graphs[gi], matched_core[gi]) for gi in range(3)]
    identical = all(np.array_equal(Ac[0], Ac[i]) for i in (1, 2))
    iso = is_iso(Ac[0], Ac[1]) and is_iso(Ac[0], Ac[2])
    edges = int(Ac[0].sum())
    print(f"[HEADLINE] N={len(matched_core[0])} edges={edges} "
          f"identical={identical} VF2={iso}", flush=True)

    # Biological cross-check on the headline circuit.
    rows = []
    sc_match = ct_match = 0
    for r in range(len(matched_core[0])):
        cells = [anns[gi][matched_core[gi][r]] for gi in range(3)]
        scs = [c["super_class"] for c in cells]
        cts = [c["cell_type"] for c in cells]
        if scs[0] and scs[0] == scs[1] == scs[2]:
            sc_match += 1
        if cts[0] and cts[0] == cts[1] == cts[2]:
            ct_match += 1
        rows.append({"row": r,
                     "root_ids": [int(nodes[gi][matched_core[gi][r]]) for gi in range(3)],
                     "super_class": scs, "cell_type": cts,
                     "nt": [c["nt"] for c in cells]})
    n = len(matched_core[0])
    print(f"[BIO] super_class concordant rows: {sc_match}/{n}  "
          f"cell_type concordant rows: {ct_match}/{n}", flush=True)

    from collections import Counter
    comp = Counter(r["super_class"][0] for r in rows)
    print(f"[BIO] FAFB super_class composition: {dict(comp)}", flush=True)

    # ---- write artifacts ----
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "frontier.json"), "w") as f:
        json.dump(frontier, f, indent=2)
    headline = {"triple": triple, "N": n, "edges": edges,
                "identical": bool(identical), "vf2_iso": bool(iso),
                "superclass_concordant_rows": sc_match,
                "celltype_concordant_rows": ct_match,
                "rows": rows}
    with open(os.path.join(ROOT, "results", "headline_circuit.json"), "w") as f:
        json.dump(headline, f, indent=2)

    import csv
    with open(os.path.join(ROOT, "network.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(triple)
        for r in rows:
            w.writerow(r["root_ids"])
    np.save(os.path.join(ROOT, "results", "headline_adjacency.npy"), Ac[0])
    print(f"wrote network.csv ({n} rows), results/*.json  total {time.time()-t0:.1f}s",
          flush=True)


if __name__ == "__main__":
    main()
