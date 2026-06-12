"""
find_circuit_typed.py — conserved-circuit search with a CELL-TYPE constraint:
matched neurons must share both wiring pattern AND cell type across all three
datasets. This yields a biologically homologous conserved circuit (same named cell
types, identical directed wiring) across sex and CNS region.

NOTE: this is an earlier frontier stage (a typed seed-sweep). The CANONICAL headline
producer is the repo-root `run.py` (APL-seeded growth → N=169). Running this script
will overwrite network.csv with the seed-sweep result; re-run `run.py` to restore the
headline artifact.

Usage:  python find_circuit_typed.py FAFB BANC MCNS
"""
from __future__ import annotations
import sys, os, json, time
import numpy as np

from io_utils import build_clean, ROOT
from graph_core import DiGraph
from iso_utils import is_iso
from annotate import load_annotations
from match_engine import (grow_common_subgraph, two_core_positions,
                          largest_weak_component_positions)


def adj(g, m):
    return g.induced_adcmatrix(m)


def norm(t: str) -> str:
    return (t or "").strip()


def main():
    triple = sys.argv[1:4] if len(sys.argv) >= 4 else ["FAFB", "BANC", "MCNS"]
    t0 = time.time()
    nodes, graphs, anns, labs = [], [], [], []
    for ds in triple:
        nd, ed = build_clean(ds)
        g = DiGraph(len(nd), ed)
        ann, _ = load_annotations(ds)
        lab = [norm(ann[i]["cell_type"]) for i in range(len(nd))]
        nodes.append(nd); graphs.append(g); anns.append(ann); labs.append(lab)
    print(f"loaded {triple} ({time.time()-t0:.1f}s)", flush=True)

    # type -> representative (highest total-degree) node per graph
    rep = []
    for gi, g in enumerate(graphs):
        by = {}
        for i in range(g.n):
            t = labs[gi][i]
            if not t or t == "nan":
                continue
            by.setdefault(t, []).append(i)
        rep.append({t: max(v, key=lambda x: g.indeg[x] + g.outdeg[x])
                    for t, v in by.items()})
    shared = set(rep[0]) & set(rep[1]) & set(rep[2])

    def minrepdeg(t):
        return min(graphs[gi].indeg[rep[gi][t]] + graphs[gi].outdeg[rep[gi][t]]
                   for gi in range(3))
    seeds_types = sorted(shared, key=lambda t: -minrepdeg(t))
    seeds_types = [t for t in seeds_types if minrepdeg(t) >= 6][:80]
    print(f"{len(shared)} shared types; trying {len(seeds_types)} seeds", flush=True)

    best = None
    t = time.time()
    for si, t_seed in enumerate(seeds_types):
        seeds = [rep[gi][t_seed] for gi in range(3)]
        m = grow_common_subgraph(graphs, seeds, max_n=80, strategy="rich",
                                 frontier_cap=1200, labels=labs)
        A0 = adj(graphs[0], m[0])
        core = two_core_positions(A0)
        if core.size:
            wcc = largest_weak_component_positions(A0[np.ix_(core, core)])
            corepos = core[wcc]
        else:
            corepos = core
        if best is None or corepos.size > best[0]:
            best = (int(corepos.size), len(m[0]), m, corepos, t_seed)
        if (si + 1) % 20 == 0:
            print(f"  ...{si+1}/{len(seeds_types)} seeds, best circuit={best[0]} "
                  f"(seed {best[4]})  ({time.time()-t:.1f}s)", flush=True)
    core_size, full_n, m, corepos, t_seed = best
    print(f"best seed-type={t_seed} full_N={full_n} circuit={core_size} "
          f"({time.time()-t:.1f}s)", flush=True)

    matched_core = [[m[gi][p] for p in corepos.tolist()] for gi in range(3)]
    Ac = [adj(graphs[gi], matched_core[gi]) for gi in range(3)]
    identical = all(np.array_equal(Ac[0], Ac[i]) for i in (1, 2))
    iso = is_iso(Ac[0], Ac[1]) and is_iso(Ac[0], Ac[2])
    edges = int(Ac[0].sum())
    n = len(matched_core[0])
    print(f"[HEADLINE-typed] N={n} edges={edges} identical={identical} VF2={iso}",
          flush=True)

    rows = []
    ct_match = 0
    for r in range(n):
        cells = [anns[gi][matched_core[gi][r]] for gi in range(3)]
        cts = [norm(c["cell_type"]) for c in cells]
        if cts[0] and cts[0] == cts[1] == cts[2]:
            ct_match += 1
        rows.append({"row": r,
                     "root_ids": [int(nodes[gi][matched_core[gi][r]]) for gi in range(3)],
                     "cell_type": cts,
                     "super_class": [c["super_class"] for c in cells],
                     "nt": [c["nt"] for c in cells]})
    print(f"[BIO] cell_type concordant rows: {ct_match}/{n}", flush=True)
    print(f"[BIO] cell types: {[r['cell_type'][0] for r in rows]}", flush=True)

    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    headline = {"triple": triple, "N": n, "edges": edges,
                "identical": bool(identical), "vf2_iso": bool(iso),
                "celltype_concordant_rows": ct_match, "seed_type": t_seed,
                "rows": rows}
    with open(os.path.join(ROOT, "results", "headline_typed.json"), "w") as f:
        json.dump(headline, f, indent=2)
    np.save(os.path.join(ROOT, "results", "headline_typed_adjacency.npy"), Ac[0])
    import csv
    with open(os.path.join(ROOT, "network.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(triple)
        for r in rows:
            w.writerow(r["root_ids"])
    print(f"wrote network.csv + results/headline_typed.json  ({time.time()-t0:.1f}s)",
          flush=True)


if __name__ == "__main__":
    main()
