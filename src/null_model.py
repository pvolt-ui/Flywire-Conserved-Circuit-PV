"""
null_model.py — significance test for the conserved circuit.

The headline claim is that a directed induced subgraph of same-typed neurons has
*byte-identical* wiring in FAFB, BANC and MCNS. The fair criticism (see review §3) is:
with thousands of interchangeable same-type neurons per dataset (e.g. ~2,200 KCg-m),
maybe *some* same-typed selection reproduces that sparse wiring purely by chance — so
"exactly isomorphic" could be expected, not surprising.

This script answers that with a **type-constrained random-matching null**:

  Fix FAFB's induced adjacency W (the template, in row order).
  For each test dataset (BANC, MCNS) and each row r (required cell type t_r), draw a
  RANDOM neuron of type t_r from that dataset (distinct across rows). Build the induced
  adjacency of the random selection in the same row order and compare to W.
  Repeat B times. p = (#trials reproducing W + 1) / (B + 1).

This conditions on the *real* graph and the *real* cell-type abundances, so it isolates
exactly the suspicious quantity: given the type pools, how easily does random same-typed
selection reproduce this exact wiring?

We also decompose the circuit into:
  - SCAFFOLD : the non-KC rows (APL + projection/local/receptor neurons), whose specific
               cross-wiring is the structurally informative part;
  - KC-FAN   : the KCg-m + APL bipartite feedback loop, where the KC pool is large and
               interchangeable.
This reveals which part carries the conservation signal.

Usage:  python src/null_model.py [n_trials]      (default 2000)
Reproducible: fixed RNG seed.
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np

from io_utils import build_clean, ROOT
from graph_core import DiGraph
from annotate import load_annotations

TRIPLE = ["FAFB", "BANC", "MCNS"]
SEED = 0


def norm(t: str) -> str:
    return (t or "").strip()


def induced_adj(G: DiGraph, idx: np.ndarray) -> np.ndarray:
    """Directed induced adjacency (uint8) on node indices `idx`, in given order."""
    return G.induced_adcmatrix([int(i) for i in idx])


def main():
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    rng = np.random.default_rng(SEED)
    t0 = time.time()

    headline = json.load(open(os.path.join(ROOT, "results", "headline_typed.json")))
    rows = headline["rows"]
    N = len(rows)
    # required cell type per row (concordant across datasets by construction)
    row_types = [norm(r["cell_type"][0]) for r in rows]
    is_kc = np.array([t.startswith("KC") for t in row_types])
    scaffold_rows = np.where(~is_kc)[0]
    print(f"circuit N={N}  scaffold(non-KC)={scaffold_rows.size}  "
          f"KC rows={int(is_kc.sum())}", flush=True)

    # load graphs + annotations, build per-dataset id->index maps and type pools
    graphs, pools, matched_idx = [], [], []
    for gi, ds in enumerate(TRIPLE):
        nd, ed = build_clean(ds)
        G = DiGraph(len(nd), ed)
        ann, _ = load_annotations(ds)
        id2idx = {int(rid): i for i, rid in enumerate(nd.tolist())}
        pool = {}
        for i in range(len(nd)):
            t = norm(ann[i]["cell_type"])
            if t and t != "nan":
                pool.setdefault(t, []).append(i)
        pool = {t: np.array(v, dtype=np.int64) for t, v in pool.items()}
        midx = np.array([id2idx[r["root_ids"][gi]] for r in rows], dtype=np.int64)
        graphs.append(G); pools.append(pool); matched_idx.append(midx)
        print(f"  {ds}: nodes={len(nd)}  matched rows mapped={len(midx)}", flush=True)

    # template W from FAFB (reference), verify against stored artifact
    W = induced_adj(graphs[0], matched_idx[0])
    stored = np.load(os.path.join(ROOT, "results", "headline_typed_adjacency.npy"))
    assert np.array_equal(W, stored), "FAFB template != stored headline adjacency!"
    print(f"template W: {N}x{N}, edges={int(W.sum())} (matches stored artifact)", flush=True)

    # report pool sizes for the required types
    print("\ntype pools (per dataset) for required types:", flush=True)
    seen = set()
    for t in row_types:
        if t in seen:
            continue
        seen.add(t)
        cnt = row_types.count(t)
        sizes = [int(pools[gi].get(t, np.array([])).size) for gi in range(3)]
        print(f"  {t:20s} need={cnt:3d}  pools FAFB/BANC/MCNS = {sizes}", flush=True)

    def run_null(test_gi, row_mask):
        """Random same-type draws in dataset test_gi over the given rows; compare the
        induced adjacency (restricted to those rows) to W restricted likewise."""
        rows_sel = np.where(row_mask)[0]
        Wsub = W[np.ix_(rows_sel, rows_sel)]
        G = graphs[test_gi]
        n_identical = 0
        best_agree = -1.0
        agree_sum = 0.0
        best_jac = -1.0
        jac_sum = 0.0
        Wedges = int(Wsub.sum())            # number of 1s in the template (constant)
        total_cells = Wsub.size - len(rows_sel)  # exclude diagonal
        Wb = Wsub.astype(bool)
        for _ in range(B):
            pick = np.empty(len(rows_sel), dtype=np.int64)
            used = set()
            ok = True
            for j, r in enumerate(rows_sel.tolist()):
                cands = pools[test_gi].get(row_types[r])
                if cands is None or cands.size == 0:
                    ok = False; break
                for _try in range(8):  # draw a distinct node of the required type
                    c = int(cands[rng.integers(cands.size)])
                    if c not in used:
                        used.add(c); pick[j] = c; break
                else:
                    ok = False; break
            if not ok:
                continue
            A = induced_adj(G, pick)
            if np.array_equal(A, Wsub):
                n_identical += 1
            agree = (A == Wsub).sum() - len(rows_sel)  # off-diagonal agreement
            frac = agree / total_cells
            agree_sum += frac
            if frac > best_agree:
                best_agree = frac
            # edge-set Jaccard (the honest metric for a sparse adjacency)
            Ab = A.astype(bool)
            inter = int((Ab & Wb).sum())
            union = int((Ab | Wb).sum())
            jac = inter / union if union else 1.0
            jac_sum += jac
            if jac > best_jac:
                best_jac = jac
        p = (n_identical + 1) / (B + 1)
        return {"n_identical": n_identical, "p": p, "template_edges": Wedges,
                "mean_edge_agreement": agree_sum / B,
                "best_edge_agreement": best_agree,
                "mean_edge_jaccard": jac_sum / B,
                "best_edge_jaccard": best_jac}

    full_mask = np.ones(N, dtype=bool)
    scaff_mask = ~is_kc

    print(f"\n=== NULL: {B} type-constrained random matchings per test dataset ===",
          flush=True)
    results = {"n_trials": B, "seed": SEED, "N": N,
               "scaffold_N": int(scaffold_rows.size), "kc_N": int(is_kc.sum()),
               "datasets": {}}
    for gi in (1, 2):  # BANC, MCNS (FAFB is the reference template)
        ds = TRIPLE[gi]
        full = run_null(gi, full_mask)
        scaff = run_null(gi, scaff_mask)
        results["datasets"][ds] = {"full_circuit": full, "scaffold_only": scaff}
        print(f"\n[{ds}]", flush=True)
        print(f"  FULL {N:<4d}: identical={full['n_identical']}/{B}  p={full['p']:.4g}  "
              f"best_edge_jaccard={full['best_edge_jaccard']:.3f}  "
              f"mean_jaccard={full['mean_edge_jaccard']:.3f}", flush=True)
        print(f"  SCAFFOLD : identical={scaff['n_identical']}/{B}  p={scaff['p']:.4g}  "
              f"best_edge_jaccard={scaff['best_edge_jaccard']:.3f}  "
              f"mean_jaccard={scaff['mean_edge_jaccard']:.3f}", flush=True)

    out = os.path.join(ROOT, "results", "null_model.json")
    json.dump(results, open(out, "w"), indent=2)
    print(f"\nsaved {out}  ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
