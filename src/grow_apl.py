"""grow_apl.py — grow the APL-seeded mushroom-body conserved circuit to its ceiling
and report structure + composition. Run with python -u.

This is the canonical headline producer; the repo-root `run.py` is a thin wrapper around
it. The other src/find_circuit*.py scripts are earlier frontier stages, not canonical."""
import os, json, time
import numpy as np
from collections import Counter
from io_utils import build_clean, ROOT
from graph_core import DiGraph
from iso_utils import is_iso
from annotate import load_annotations
from match_engine import (grow_common_subgraph, two_core_positions,
                          largest_weak_component_positions)

triple = ["FAFB", "BANC", "MCNS"]
nodes, graphs, anns, labs = [], [], [], []
for ds in triple:
    nd, ed = build_clean(ds)
    g = DiGraph(len(nd), ed)
    ann, _ = load_annotations(ds)
    nodes.append(nd); graphs.append(g); anns.append(ann)
    labs.append([(ann[i]["cell_type"] or "").strip() for i in range(len(nd))])
print("loaded", flush=True)

# representative APL (highest-degree neuron of type APL) per graph
def rep_of(t, gi):
    cands = [i for i in range(graphs[gi].n) if labs[gi][i] == t]
    return max(cands, key=lambda x: graphs[gi].indeg[x] + graphs[gi].outdeg[x])

seeds = [rep_of("APL", gi) for gi in range(3)]
print("APL seeds:", [int(nodes[gi][seeds[gi]]) for gi in range(3)], flush=True)

t = time.time()
m = grow_common_subgraph(graphs, seeds, max_n=600, strategy="rich",
                         frontier_cap=3000, labels=labs)
A0 = graphs[0].induced_adcmatrix(m[0])
core = two_core_positions(A0)
wcc = largest_weak_component_positions(A0[np.ix_(core, core)])
corepos = core[wcc]
print(f"full_N={len(m[0])} 2core_WCC={corepos.size} ({time.time()-t:.1f}s)", flush=True)

matched = [[m[gi][p] for p in corepos.tolist()] for gi in range(3)]
Ac = [graphs[gi].induced_adcmatrix(matched[gi]) for gi in range(3)]
identical = all(np.array_equal(Ac[0], Ac[i]) for i in (1, 2))
iso = is_iso(Ac[0], Ac[1]) and is_iso(Ac[0], Ac[2])
n = len(matched[0]); A = Ac[0]
print(f"N={n} edges={int(A.sum())} identical={identical} VF2={iso}", flush=True)

types = [(anns[0][matched[0][r]]["cell_type"] or "").strip() for r in range(n)]
print("composition:", dict(Counter(types)), flush=True)
indeg = A.sum(0); outdeg = A.sum(1)
recip = int(((A == 1) & (A.T == 1)).sum() // 2)
print(f"min_total_deg={int((indeg+outdeg).min())} mean_deg={(indeg+outdeg).mean():.2f} "
      f"reciprocal_pairs={recip}", flush=True)
# non-KC nodes and their NT
for r in range(n):
    if not types[r].startswith("KC"):
        c = anns[0][matched[0][r]]
        print(f"  non-KC: {types[r]:18s} sc={c['super_class']:18s} nt={c['nt']} "
              f"in={int(indeg[r])} out={int(outdeg[r])}", flush=True)

# save as headline
rows = []
for r in range(n):
    cells = [anns[gi][matched[gi][r]] for gi in range(3)]
    rows.append({"row": r,
                 "root_ids": [int(nodes[gi][matched[gi][r]]) for gi in range(3)],
                 "cell_type": [(c["cell_type"] or "").strip() for c in cells],
                 "super_class": [c["super_class"] for c in cells],
                 "nt": [c["nt"] for c in cells]})
headline = {"triple": triple, "N": n, "edges": int(A.sum()),
            "identical": bool(identical), "vf2_iso": bool(iso),
            "celltype_concordant_rows": n, "seed_type": "APL", "rows": rows}
os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
json.dump(headline, open(os.path.join(ROOT, "results", "headline_typed.json"), "w"),
          indent=2)
np.save(os.path.join(ROOT, "results", "headline_typed_adjacency.npy"), A)
import csv
with open(os.path.join(ROOT, "network.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(triple)
    for r in rows:
        w.writerow(r["root_ids"])
print("saved headline + network.csv", flush=True)
