"""
connectivity_stats.py — corroborate the conserved motif with per-cell-type connection
PROBABILITIES across the three full connectomes (the prediction stated in science.md).

Within the matched circuit, per-type wiring is identical across datasets *by construction*
(that is the isomorphism). The non-trivial, non-circular test is whether the same
connection statistics hold across the FULL neuron populations of each type in each dataset:

  * PN->KC convergence : P(edge) between all projection neurons of the circuit's PN types
                         and all KCg-m, per dataset. (Caron et al. 2013: individual PN->KC
                         partners are idiosyncratic, but the convergence RATE is stable.)
  * APL->KC / KC->APL coverage : fraction of all KCg-m that receive / send an APL connection.

If these probabilities agree across FAFB/BANC/MCNS (computed over the whole populations,
not the matched subset), the conserved motif is corroborated at the population level, not
just in the hand-matched circuit.

Usage:  python src/connectivity_stats.py
"""
from __future__ import annotations
import os, json, time
import numpy as np

from io_utils import build_clean, ROOT
from graph_core import DiGraph
from annotate import load_annotations

TRIPLE = ["FAFB", "BANC", "MCNS"]


def norm(t):
    return (t or "").strip()


def edge_prob(G: DiGraph, src: np.ndarray, dst: np.ndarray) -> float:
    """P(edge) from set src to set dst = (#present ordered pairs) / (|src|*|dst|)."""
    if src.size == 0 or dst.size == 0:
        return float("nan")
    uu = np.repeat(src, dst.size)
    vv = np.tile(dst, src.size)
    keys = (uu.astype(np.int64) << 32) | vv.astype(np.int64)
    present = G.has_edges(keys)
    return float(present.sum()) / (src.size * dst.size)


def coverage(G: DiGraph, hub: np.ndarray, pool: np.ndarray, direction: str) -> float:
    """Fraction of `pool` nodes connected to ANY hub node, in given direction."""
    if pool.size == 0 or hub.size == 0:
        return float("nan")
    hset = set(hub.tolist())
    hit = 0
    for p in pool.tolist():
        nb = (G.in_neighbors(p) if direction == "from_hub" else G.out_neighbors(p))
        if hset & set(nb.tolist()):
            hit += 1
    return hit / pool.size


def main():
    t0 = time.time()
    H = json.load(open(os.path.join(ROOT, "results", "headline_typed.json")))
    rows = H["rows"]
    row_types = [norm(r["cell_type"][0]) for r in rows]
    pn_types = sorted({t for t in row_types if "PN" in t})
    print(f"PN types in circuit: {pn_types}", flush=True)

    stats = {"pn_types": pn_types, "datasets": {}}
    for gi, ds in enumerate(TRIPLE):
        nd, ed = build_clean(ds)
        G = DiGraph(len(nd), ed)
        ann, _ = load_annotations(ds)
        lab = np.array([norm(ann[i]["cell_type"]) for i in range(len(nd))])

        def pool(types):
            return np.array([i for i in range(len(nd)) if lab[i] in types],
                            dtype=np.int64)

        kcg = pool({"KCg-m"})
        pn = pool(set(pn_types))
        apl = pool({"APL"})
        p_pn_kc = edge_prob(G, pn, kcg)
        cov_apl_to_kc = coverage(G, apl, kcg, "from_hub")   # APL -> KC
        cov_kc_to_apl = coverage(G, apl, kcg, "to_hub")     # KC -> APL
        stats["datasets"][ds] = {
            "n_KCg_m": int(kcg.size), "n_PN_circuit_types": int(pn.size),
            "n_APL": int(apl.size),
            "P_PN_to_KCg_m": p_pn_kc,
            "APL_to_KCg_m_coverage": cov_apl_to_kc,
            "KCg_m_to_APL_coverage": cov_kc_to_apl}
        print(f"[{ds}] KCg-m={kcg.size} PN={pn.size} APL={apl.size}  "
              f"P(PN->KC)={p_pn_kc:.4f}  APL->KC cov={cov_apl_to_kc:.3f}  "
              f"KC->APL cov={cov_kc_to_apl:.3f}", flush=True)

    json.dump(stats, open(os.path.join(ROOT, "results", "connectivity_stats.json"), "w"),
              indent=2)
    print(f"\nsaved results/connectivity_stats.json  ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
