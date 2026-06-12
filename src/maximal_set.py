"""
maximal_set.py — the OTHER end of the degeneracy frontier: the *largest* cell-type-
conserved isomorphic structure, not just the rich 2-core circuit.

The headline circuit keeps ONE representative neuron per (attachment-signature, cell-type)
key. But many same-typed neurons share a signature — e.g. hundreds of KCg-m all attach to
APL the same way. Those are mutually interchangeable members of the SAME conserved
structure. This script reports how large the conserved set becomes once we keep *all* of
them (bounded per dataset by the scarcest dataset, since an isomorphism needs a bijection).

Method:
  1. Take the headline circuit's SCAFFOLD = its non-KC nodes (APL + PN/LN/ORN/HRN core),
     fixed per dataset in row order. The scaffold sub-block is byte-identical across
     datasets (it is a sub-matrix of the verified headline adjacency).
  2. For every neuron of a Kenyon-cell type in each dataset, compute its attachment
     signature to the scaffold. Group by (signature, cell_type).
  3. NAIVE count (an UPPER estimate): for each signature-class present in all three
     datasets, min(count_FAFB, count_BANC, count_MCNS) interchangeable copies. This
     IGNORES KC<->KC edges, so it overcounts -- two same-class KCs are only truly
     interchangeable if their mutual wiring also replicates, which it generally does not.
  4. VERIFIED set (the number we report): actually BUILD the conserved set -- start from
     the scaffold and add KC triples one class at a time, keeping a triple only if each
     member is non-adjacent to every already-added KC in its own graph (a true independent
     fan, so the KC<->KC block is empty in all three datasets). The resulting induced
     subgraph is then re-checked for byte-identity AND exact VF2 isomorphism across all
     three datasets. This is a genuine, verified lower bound on the largest cell-type-
     conserved mutually-isomorphic structure.

In practice the naive count (~707) overcounts the verified figure (~221) by ~3x: this gap
is the whole point -- counting interchangeable slots is not the same as a verified
isomorphic subgraph, and we report only what VF2 confirms.

Usage:  python src/maximal_set.py
"""
from __future__ import annotations
import os, json, time
from collections import Counter
import numpy as np

from io_utils import build_clean, ROOT
from graph_core import DiGraph
from annotate import load_annotations
from iso_utils import is_iso
from match_engine import _attach_sigs_batch

TRIPLE = ["FAFB", "BANC", "MCNS"]


def norm(t):
    return (t or "").strip()


def main():
    t0 = time.time()
    H = json.load(open(os.path.join(ROOT, "results", "headline_typed.json")))
    rows = H["rows"]
    row_types = [norm(r["cell_type"][0]) for r in rows]
    is_kc = [t.startswith("KC") for t in row_types]
    scaffold_rows = [i for i in range(len(rows)) if not is_kc[i]]
    kc_types = sorted({row_types[i] for i in range(len(rows)) if is_kc[i]})
    print(f"headline N={len(rows)}  scaffold={len(scaffold_rows)}  "
          f"KC rows={sum(is_kc)}  KC types={kc_types}", flush=True)

    graphs, labs, scaff_idx = [], [], []
    for gi, ds in enumerate(TRIPLE):
        nd, ed = build_clean(ds)
        G = DiGraph(len(nd), ed)
        ann, _ = load_annotations(ds)
        lab = [norm(ann[i]["cell_type"]) for i in range(len(nd))]
        id2idx = {int(rid): i for i, rid in enumerate(nd.tolist())}
        sc = np.array([id2idx[rows[r]["root_ids"][gi]] for r in scaffold_rows],
                      dtype=np.int64)
        graphs.append(G); labs.append(lab); scaff_idx.append(sc)
        print(f"  {ds}: nodes={len(nd)}", flush=True)

    # sanity: KC<->KC induced edges within the headline matched KCs (small, identical)
    kc_kc = None
    for gi, ds in enumerate(TRIPLE):
        id2idx = {int(rid): i for i, rid in enumerate(build_clean(ds)[0].tolist())}
        kc_nodes = [id2idx[rows[r]["root_ids"][gi]] for r in range(len(rows)) if is_kc[r]]
        A = graphs[gi].induced_adcmatrix(kc_nodes)
        kc_kc = int(A.sum())
        print(f"  {ds}: KC<->KC induced edges among matched KCs = {kc_kc}",
              flush=True)

    # signature classes of all KC-type neurons relative to the scaffold, per dataset.
    # Keep the actual node lists per class (not just counts) so we can BUILD and VERIFY
    # the conserved set, rather than merely counting interchangeable slots.
    counts, classnodes = [], []
    for gi, ds in enumerate(TRIPLE):
        kc_all = np.array([i for i in range(graphs[gi].n)
                           if labs[gi][i] in kc_types], dtype=np.int64)
        sigs, ec = _attach_sigs_batch(graphs[gi], kc_all, scaff_idx[gi])
        c = Counter()
        nodes_by_key = {}
        for i, x in enumerate(kc_all.tolist()):
            if ec[i] == 0:               # must attach to the scaffold
                continue
            key = (sigs[i], labs[gi][x])
            c[key] += 1
            nodes_by_key.setdefault(key, []).append(x)
        for k in nodes_by_key:
            nodes_by_key[k].sort()
        counts.append(c)
        classnodes.append(nodes_by_key)
        print(f"  {ds}: KC neurons attaching to scaffold = {sum(c.values())} "
              f"in {len(c)} signature-classes", flush=True)

    common = sorted(set(counts[0]) & set(counts[1]) & set(counts[2]))
    naive_added = sum(min(counts[0][k], counts[1][k], counts[2][k]) for k in common)
    naive_N = len(scaffold_rows) + naive_added
    print(f"\ncommon KC signature-classes across 3 datasets: {len(common)}", flush=True)
    print(f"NAIVE count (bijection-bounded, KC<->KC edges IGNORED): N <= {naive_N} "
          f"(scaffold {len(scaffold_rows)} + KC fan {naive_added})", flush=True)

    # ---- VERIFIED construction --------------------------------------------------
    # The naive count assumes every same-(signature,type) KC is interchangeable, which
    # is only true if the KC<->KC block also replicates across datasets. It does NOT in
    # general, so the naive number OVERCOUNTS. We therefore actually BUILD a conserved
    # set and require byte-identical induced adjacency:
    #   start from the (already-identical) scaffold, then add KC triples one class at a
    #   time, keeping a triple only if each member is non-adjacent to every already-added
    #   KC in its own graph (a true independent fan). Then the KC<->KC block is empty in
    #   all three datasets and the scaffold attachment is identical by signature-class, so
    #   the induced subgraph stays byte-identical -- which we re-verify with VF2 below.
    matched = [list(scaff_idx[gi].tolist()) for gi in range(3)]
    added_kc = [set() for _ in range(3)]
    verified_added = 0
    for k in common:
        m = min(len(classnodes[gi][k]) for gi in range(3))
        for j in range(m):
            trip = [classnodes[gi][k][j] for gi in range(3)]
            ok = True
            for gi in range(3):
                x = trip[gi]; G = graphs[gi]
                nb = set(G.out_neighbors(x).tolist()) | set(G.in_neighbors(x).tolist())
                if nb & added_kc[gi]:
                    ok = False; break
            if ok:
                for gi in range(3):
                    matched[gi].append(trip[gi]); added_kc[gi].add(trip[gi])
                verified_added += 1

    Av = [graphs[gi].induced_adcmatrix(matched[gi]) for gi in range(3)]
    identical = all(np.array_equal(Av[0], Av[i]) for i in (1, 2))
    vf2 = is_iso(Av[0], Av[1]) and is_iso(Av[0], Av[2])
    verified_N = len(matched[0])
    verified_edges = int(Av[0].sum())
    assert identical and vf2, "verified maximal set is NOT isomorphic -- aborting"
    print(f"=> VERIFIED maximal cell-type-conserved set: N = {verified_N} "
          f"(scaffold {len(scaffold_rows)} + {verified_added} KC fan), "
          f"edges={verified_edges}, byte-identical={identical}, VF2={vf2}", flush=True)
    print(f"   (naive count {naive_N} overcounts {naive_N/verified_N:.1f}x because it "
          f"ignores the KC<->KC block; we report only the VF2-verified figure)", flush=True)

    out = {"scaffold_N": len(scaffold_rows), "kc_types": kc_types,
           "kc_kc_edges_in_core": kc_kc,
           "common_kc_signature_classes": len(common),
           "naive_kc_copies": int(naive_added), "naive_count_N": int(naive_N),
           "verified_kc_copies": int(verified_added), "verified_N": int(verified_N),
           "verified_edges": verified_edges,
           "verified_identical": bool(identical), "verified_vf2_iso": bool(vf2),
           "per_dataset_kc_attaching": [int(sum(c.values())) for c in counts],
           "note": "verified_N is built as scaffold + an independent KC fan and is "
                   "byte-identical + VF2-isomorphic across all 3 datasets (a true lower "
                   "bound). naive_count_N is an UPPER estimate that ignores KC<->KC edges "
                   "and is NOT isomorphic as-is; it overcounts. Report verified_N."}
    json.dump(out, open(os.path.join(ROOT, "results", "maximal_set.json"), "w"),
              indent=2)
    print(f"saved results/maximal_set.json  ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
